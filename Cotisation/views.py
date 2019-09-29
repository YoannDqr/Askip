# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from reportlab.pdfgen import canvas
import pdfkit
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from datetime import date


@login_required(login_url="/")
def index(request):
	"""
	Back end login page
    :param request:
    :return:
    """
	if request.method == "POST":
		POST = request.POST
		if 'association' in POST and 'password' in POST:
			# Check user credential if the formular has been filled
			try:
				association = Association.objects.get(nom=POST['association'], mdp=POST['password'])
			except:
				if POST['association'] == 'NC':
					error = ['Login incorrect... L\'association choisi n\'existe pas']
				else:
					error = ['Login incorrect...']

				associations = Association.objects.all()
				return render(request, "cotisation/login.html", {
					'associations': associations,
					'error': error
				})

			# Drop a session cookie
			request.session['association_user'] = POST['association']
			return redirect('cotisation.dashboard', association=association.nom)
		else:
			association = Association.objects.all()
			return render(request, "cotisation/login.html", locals())

	elif not ('association_user' in request.session):
		# If invalid credentials and not adapted session cookie, user is redirected to login page
		associations = Association.objects.all()
		return render(request, "cotisation/login.html", {'associations':associations})

	else:
		return redirect('cotisation.dashboard', association=request.session['association_user'])


@login_required(login_url="/")
def checkout(request):
	if 'association_user' in request.session:
		del request.session['association_user']

	return redirect('cotisation.index')


@login_required(login_url="/")
def dashboard(request, association=""):
	"""
    Page to manage your association
    :param request: Http request
    :param association: Association id
    :return: cotisation.html
    """
	erreur = []
	if request.session.has_key("association_user") and request.session["association_user"] == association:
		association = get_object_or_404(Association, nom=association)
		user = get_object_or_404(Utilisateur, pk=request.user.pk)
		user_mdp = is_gestionnaire_mdp(user, association)
		user_treso = is_gestionnaire_treso(user, association) or is_reader_treso(user, association)

		# Test formular answers and process data
		perform_formular(request, association)

		# Users who aren't association's contributor
		utilisateurs = Utilisateur.objects.all()
		for utilisateur in utilisateurs:
			for cotisant in association.cotisant.all():
				if utilisateur == cotisant.personne:
					utilisateurs = utilisateurs.exclude(pk=utilisateur.pk)

		# User who are association's contributor
		cotisant = association.cotisant.all()

		# Expenditures of the association
		depenses = Depense.objects.filter(association=association).order_by('date')

		# Way of payement of these expenditures
		moyens = []

		# Categorie of these expenditures
		categories = []

		# Association balance
		solde = 0

		for depense in depenses:
			if not (depense.moyen in moyens):
				moyens.append(depense.moyen)
			if not (depense.categorie in categories):
				categories.append(depense.categorie)
			solde += depense.montant

		votes = Vote.objects.filter(association=association)
		events = Evenement.objects.all().order_by('startDate')

		return render(request, "cotisation/cotisation.html", {
			'association': association,
			'user_mdp': user_mdp,
			'user_treso': user_treso,
			'votes': votes,
			'events': events,
			'categories': categories,
			'moyens': moyens,
			'depenses': depenses,
			'cotisant': cotisant,
			'utilisateurs': utilisateurs,
		})
	else:
		return redirect('cotisation.index')


def is_gestionnaire_treso(user, association):
	for poste in user.poste.all():
		if poste.gestionnaire_tresorerie:
			return True
	return False


def is_gestionnaire_mdp(user, association):
	for poste in user.poste.all():
		if poste.gestionnaire_mdp:
			return True
	return False


def is_reader_treso(user, association):
	for poste in user.poste.all():
		if poste.reader_tresorerie:
			return True
	return False


@login_required(login_url="/")
def perform_formular(request, association):
	"""
    Validate and perform formular related action
    :param request:
    :param association: id of the current association
    :return: void
    """

	################################################################################################################
	#                                                                                                              #
	#                               Begin formulars processing                                                     #
	#                               ==========================                                                     #
	#              - 'new picture'      :   change the association profil picture                           ;      #
	#              - 'personne_id'      :   add a new contributor                                           ;      #
	#              - 'tresorerie'       :   formulare related to tresuary                                   ;      #
	#              - 'club'             :   create a club                                                   ;      #
	#              - 'votes'            :   formular related to polls edition                               ;      #
	#              - 'poste_titre'      :   formular related to association's positions                     ;      #
	#              - 'event'            :   formular related to event                                       ;      #
	#              - 'parametre'        :   formular related to association profil configuration            ;      #
	#                                                                                                              #
	################################################################################################################

	erreur = []
	user = get_object_or_404(Utilisateur, pk=request.user.pk)

	# Change the picture of the association
	if 'new_picture' in request.FILES:
		association.logo = request.FILES['new_picture']
		association.save()

	if request.method == "POST":
		# Add a contributor
		if 'personne_id' in request.POST:
			new_user = get_object_or_404(Utilisateur, pk=request.POST['personne_id'])
			cotisation = Cotisation(personne=new_user, association=association, stade=0)
			cotisation.save()

		# Treasury Formular
		elif 'tresorerie' in request.POST and is_gestionnaire_treso(user, association):

			# New expenditure
			if not ('modify' in request.POST):
				if (
						'categorie' in request.POST and
						'date' in request.POST and
						'obj' in request.POST and
						'montant' in request.POST and
						'moyen_paye' in request.POST
				):
					if request.POST['moyen_paye'] == 'NC':  # Si on crée un nouveau moyen de payement
						if 'new_moyen' in request.POST and request.POST['new_moyen'] != "":
							moyen = request.POST['new_moyen']
						else:
							moyen = ""
					else:
						moyen = request.POST['moyen_paye']

					# New payement categorie
					if request.POST['categorie'] == 'NC':
						if 'new_categorie' in request.POST and request.POST['new_categorie'] != "":
							categorie = request.POST['new_categorie']
						else:
							categorie = ""
					else:
						categorie = request.POST['categorie']
					if moyen != "" and categorie != "":
						new_depense = Depense(
							modifier=user,
							association=association,
							date=request.POST['date'],
							sujet=request.POST['obj'],
							montant=request.POST['montant'],
							categorie=categorie,
							moyen=moyen
						)
						new_depense.save()
					else:
						erreur.append("Moyen de payement ou catégorie non valide")

				else:
					erreur.append("Données manquantes")

		# Club Formular
		elif (
				'club' in request.POST and
				'nom_club' in request.POST and
				'administrateur_club' in request.POST
		):
			user = get_object_or_404(Cotisation, pk=request.POST["administrateur_club"])
			if 'description_club' in request.POST:
				description = request.POST['description_club']
			else:
				description = " "
			if 'prix_club' in request.POST and request.POST["prix_club"] != "":
				prix = request.POST["prix_club"]
			else:
				prix = 0
			club = Club(
				nom=request.POST['nom_club'],
				description=description,
				prix_cotisation=prix,
				association=association
			)
			club.save()
			club.administrateurs.add(user)
			club.save()

		# Polls formular
		elif (
				'votes' in request.POST and
				'accessibility' in request.POST and
				'question' in request.POST and
				'startDate' in request.POST and
				'endDate' in request.POST and
				'reponse_vote_0' in request.POST and
				'reponse_vote_1' in request.POST
		):
			question = Vote(
				association=association,
				accessibility=request.POST['accessibility'],
				startDate=request.POST['startDate'],
				endDate=request.POST['endDate'],
				question=request.POST['question'])
			question.save()
			for key, value in request.POST.items():
				if "reponse_vote_" in key and value != "":
					reponse = Reponse(reponse=value)
					reponse.save()
					question.reponse.add(reponse)
			question.save()

		# Position formular
		elif 'poste_titre' in request.POST:
			if len(Poste.objects.filter(association=association, titre=request.POST['poste_titre'])) == 0:
				new_poste = Poste(association=association, titre=request.POST['poste_titre'], ca='ca' in request.POST)
				new_poste.save()
				new_poste.create_hierachie()
				poste = new_poste
			else:
				poste = Poste.objects.get(titre=request.POST['poste_titre'], association=association)

			if request.POST.has_key('description'):
				poste.description = request.POST['description']

			if request.POST.has_key('ca'):
				poste.ca = True
			else:
				poste.ca = False
			poste.save()

		# Event Formular
		elif 'new_event' in request.POST and 'description' in request.POST and 'prix' in request.POST:
			if 'nb_place' in request.POST:
				nb_place = request.POST['nb_place']
			else:
				nb_place = 0
			if 'startDate' in request.POST:
				start_date_user = request.POST['startDate']
			else:
				start_date_user = ""
			if 'endDate' in request.POST:
				end_date_user = request.POST['endDate']
			else:
				end_date_user = ""
			evenement = Evenement(
				association=association,
				nom=request.POST['nom'],
				description=request.POST['description'],
				startDate=start_date_user,
				endDate=end_date_user,
				prix=request.POST['prix'],
				nombre_place=nb_place,
				cotisant='cotisant' in request.POST
			)
			evenement.save()

		# Paramter Formular
		elif 'parametre' in request.POST:
			# If modules are changed, just module whose checkbox is checked will be add to the association
			association.module_tresorerie = False
			association.module_club = False
			association.module_evenement = False
			association.module_vote = False
			association.module_vente = False

			if (
					is_gestionnaire_mdp(user, association) and
					request.POST.has_key('old_mdp') and
					request.POST.has_key('new_mdp') and
					request.POST['old_mdp'] == association.mdp
			):
				association.mdp = request.POST['new_mdp']
			for key, value in request.POST.items():
				if 'gestion_treso' in key and is_gestionnaire_treso(user, association):
					poste = get_object_or_404(Poste, pk=value)
					poste.gestionnaire_tresorier = True
				elif 'gestion_mdp' in key and is_gestionnaire_mdp(user, association):
					poste = get_object_or_404(Poste, pk=value)
					poste.gestionnaire_mdp = True
				elif (
						'supprime_droit_treso' in key and
						value != "NULL" and
						is_gestionnaire_treso(user, association) and
						len(association.gestionnaire_tresorerie()) > 1
				):
					poste = get_object_or_404(Poste, pk=value)
					poste.gestionnaire_tresorier = False
				elif (
						'supprime_droit_mdp' in key and
						value != "NULL" and
						is_gestionnaire_mdp(user, association) and
						len(association.gestionnaire_mdp()) > 1
				):
					poste = get_object_or_404(Poste, pk=value)
					poste.gestionnaire_mdp = False
				elif 'module_treso' in key and is_gestionnaire_treso(user, association):
					association.module_tresorerie = True
					association.save()
				elif 'module_vote' in key:
					association.module_vote = True
					association.save()
				elif 'module_club' in key:
					association.module_club = True
					association.save()
				elif 'module_event' in key:
					association.module_evenement = True
					association.save()
				elif 'module_vente' in key:
					association.module_vente = True
					association.save()
				elif 'description' in key:
					association.description = value
					association.save()
				try:
					poste.save()
				except:
					pass
			association.save()


################################################################################################################
#                                                                                                              #
#                               End formulars processing                                                       #
#                               ==========================                                                     #
#                                                                                                              #
################################################################################################################


@login_required(login_url="/")
def modify(request, association="", cotisant=""):
	if request.session.has_key("association_user") and request.session["association_user"] == association:
		cotisant = get_object_or_404(Cotisation, pk=cotisant)

		if request.method == "POST" and 'poste' in request.POST:
			# Si jamais on est dans le cas d'un NC
			try:
				asso = get_object_or_404(Association, nom=association)
				Poste.objects.get(personne=cotisant.personne, association=asso).personne.remove(cotisant.personne)
			except:
				pass
			if not request.POST['poste'] in ['NC', '-1']:
				poste = get_object_or_404(Poste, pk=request.POST['poste'])
				poste.personne.add(cotisant.personne)
				poste.save()

			# Position creation on the fly
			elif request.POST['poste'] == '-1' and 'titre' in request.POST and request.POST['titre'] != '':
				passe = False
				for titre in Poste.objects.filter(association=get_object_or_404(Association, nom=association)):
					if titre.titre == request.POST['titre']:
						passe = True
						titre.personne.add(cotisant.personne)
						titre.save()

				if not passe:
					poste = Poste(
						titre=request.POST['titre'],
						association=get_object_or_404(Association, nom=association)
					)
					poste.save()
					poste.personne.add(cotisant.personne)
					poste.save()
					poste.create_hierachie()

		postes = Poste.objects.filter(association=get_object_or_404(Association, nom=association))

		return render(request, "cotisation/modify.html", locals())
	else:
		return redirect('cotisation.index')


@login_required(login_url="/")
def modify_club(request, club="", association=""):
	if request.session.has_key('association_user') and request.session['association_user'] == association:
		club = get_object_or_404(Club, pk=club)
		association = get_object_or_404(Association, nom=association)

		if request.method == "POST":
			if request.POST.has_key('add_administrateur') and request.POST['add_administrateur'] != "NC":
				new_admin = get_object_or_404(Cotisation, pk=request.POST['add_administrateur'])
				club.administrateurs.add(new_admin)
			for key, value in request.POST.items():
				if 'remove_administrateur' in key and value != "NC":
					old_admin = get_object_or_404(Cotisation, pk=value)
					club.administrateurs.remove(old_admin)
			club.save()
		return render(request, "cotisation/modifyclub.html", locals())
	else:
		return redirect('cotisation.index')


def modify_vote(request, association="", vote=""):
	vote = get_object_or_404(Vote, pk=vote)
	return render(request, "cotisation/modifyvote.html", locals())


@login_required(login_url="/")
def reset(request, association="", cotisant=""):
	cotisation = get_object_or_404(Cotisation, pk=cotisant)
	if cotisation.stade == 1:
		cotisation.stade = 0
		cotisation.save()
		depense = Depense.objects.filter(
			association=cotisation.association,
			montant=cotisation.association.prix_cotisation,
			categorie="Cotisation"
		)
		if len(depense) > 0:
			depense[0].delete()
		else:
			erreur = "La cotisation n'a pas pu etre déduite. Veuillez le faire manuellement"
			Erreur = True
	return redirect('cotisation.modify', cotisant=cotisation.pk, association=association)


@login_required(login_url="/")
def paye(request, association="", cotisant=""):
	cotisation = get_object_or_404(Cotisation, pk=cotisant)
	if cotisation.stade == 0:
		cotisation.stade = 1
		depense = Depense(
			association=get_object_or_404(Association, nom=association),
			date=timezone.now(),
			sujet="Cotisation " + cotisation.personne.last_name,
			montant=cotisation.association.prix_cotisation,
			categorie="Cotisation",
			moyen="Payement en ligne"
		)
		depense.save()
	cotisation.save()
	return redirect('cotisation.modify', cotisant=cotisation.pk, association=association)


@login_required(login_url="/")
def generation(request, association="", cotisant=""):
	# Create a URL of our project and go to the template route

	projectUrl = "http://" + request.get_host() + reverse('cotisation.fiche-cotisation', args=cotisant)
	pdf = pdfkit.from_url(projectUrl, False)
	# Generate download
	response = HttpResponse(pdf, content_type='application/pdf')
	cotisant = get_object_or_404(Cotisation, pk=cotisant)
	response[
		'Content-Disposition'] = 'attachment; filename="' + cotisant.association.nom + '_' + cotisant.personne.last_name + '.pdf"'

	return response


@login_required(login_url="/")
def fiche(request, cotisant=""):
	cotisant = get_object_or_404(Cotisation, pk=cotisant)
	date = timezone.now()
	return render(request, "cotisation/fiche.html", locals())


def format_poste(poste):
	string = "<strong>" + poste.titre + "</strong><br>"
	for personne in poste.personne.all():
		string += personne.first_name + " " + personne.last_name + "<br>"
	return string


@login_required(login_url="/")
def hierarchie(request, association=""):
	"""
    Collects information needed to display the organigramme of the association
    :param request:
    :param association:
    :return: hierarchie.html
    """

	if (
			request.method == "POST" and
			'association_user' in request.session and
			request.session["association_user"] == association
	):
		if 'add_son' in request.POST and 'son' in request.POST:
			poste_vise = get_object_or_404(Poste, pk=request.POST['add_son'])
			poste_son = get_object_or_404(Poste, pk=request.POST['son'])
			hierarchie_vise = poste_vise.poste
			hierarchie_vise.fils.add(poste_son)
			hierarchie_vise.save()
		elif 'del_node' in request.POST:
			poste_vise = get_object_or_404(Poste, pk=request.POST['del_node'])
			hierachie_vise = poste_vise.poste
			for elt in Hierarchie.objects.all():
				if poste_vise in elt.fils.all():
					elt.fils.remove(poste_vise)
				elt.save()
			for elt in hierachie_vise.fils.all():
				hierachie_vise.fils.remove(elt)
			hierachie_vise.save()

	poste = Poste.objects.filter(association=get_object_or_404(Association, pk=association))
	root_poste = Poste.objects.get(titre="President", association=get_object_or_404(Association, pk=association))
	data = [{'id': root_poste.pk, 'name': format_poste(root_poste), 'parent': 0}]
	compteur = 1

	already_use = [root_poste.pk]
	for post in poste:

		try:
			poste_hierarchie = Hierarchie.objects.get(poste=post)
			for node_visite in poste_hierarchie.fils.all():
				data.append({
					'id': node_visite.pk,
					'name': format_poste(node_visite),
					'parent': poste_hierarchie.poste.pk}
				)
				if not (node_visite.pk in already_use):
					already_use.append(node_visite.pk)
		except:
			pass

	return render(request, "cotisation/hierarchie.html", locals())


@login_required(login_url="/")
def action(request, association=""):
	"""
    Process action related to the selects input in cotsiation.html
    :param request:
    :param association:
    :return:
    """
	user = get_object_or_404(Utilisateur, pk=request.user.pk)
	asso = get_object_or_404(Association, nom=association)

	if 'action_cotisant' in request.POST:
		if request.POST['action'] == '1':
			for key, value in request.POST.items():
				if "check" in key:
					Cotisation.objects.get(pk=value).delete()

	if 'action_tresorerie' in request.POST and is_gestionnaire_treso(user, asso):
		if request.POST['action'] == '1':
			for key, value in request.POST.items():
				if "check" in key:
					Depense.objects.get(pk=value).delete()

	if 'action_club' in request.POST:
		if request.POST['action'] == '1':
			for key, value in request.POST.items():
				if "check" in key:
					Club.objects.get(pk=value).delete()

	if 'action_vote' in request.POST:
		if request.POST['action'] == '1':
			for key, value in request.POST.items():
				if "check" in key:
					vote = Vote.objects.get(pk=value)
					for reponse in vote.reponse.all():
						reponse.delete()
					vote.delete()
		elif request.POST['action'] == '2':
			for key, value in request.POST.items():
				if "check" in key:
					vote = Vote.objects.get(pk=value)
					vote.endDate = timezone.now()
					vote.save()

	if 'action_poste' in request.POST:
		if request.POST['action'] == '1':
			for key, value in request.POST.items():
				if "check" in key:
					poste = Poste.objects.get(pk=value)
					poste.poste.delete()
					poste.delete()

		elif request.POST['action'] == '2':
			for key, value in request.POST.items():
				if "check" in key:
					poste = Poste.objects.get(pk=value)
					poste.ca = not poste.ca
					poste.save()

		elif request.POST['action'] == '3' and is_gestionnaire_treso(user, asso):
			for poste in Poste.objects.filter(association=asso):
				poste.reader_tresorerie = False
				poste.save()
			for key, value in request.POST.items():
				if 'read_treso' in key:
					poste = Poste.objects.get(pk=value)
					poste.reader_tresorerie = True
					poste.save()

	if 'action_event' in request.POST:
		if request.POST['action'] == '1':
			for key, value in request.POST.items():
				if "check" in key:
					Evenement.objects.get(pk=value).delete()

	return redirect('cotisation.dashboard', association=association)


@login_required(login_url="/")
def date(request):
	if request.method == "POST":
		if 'id' in request.POST and 'data' in request.POST:
			depense = get_object_or_404(Depense, pk=request.POST['id'])
			depense.date = request.POST['data']
			if is_gestionnaire_treso(get_object_or_404(Utilisateur, pk=request.user.pk), depense.association):
				depense.modifier = get_object_or_404(Utilisateur, pk=request.user.pk)
				depense.save()
	return HttpResponse(status=200, content_type="application/json")


@login_required(login_url="/")
def sujet(request):
	if request.method == "POST":
		if 'id' in request.POST and 'data' in request.POST:
			depense = get_object_or_404(Depense, pk=request.POST['id'])

			depense.sujet = request.POST['data']
			if is_gestionnaire_treso(get_object_or_404(Utilisateur, pk=request.user.pk), depense.association):
				depense.modifier = get_object_or_404(Utilisateur, pk=request.user.pk)
				depense.save()
	return HttpResponse(status=200, content_type="application/json")


@login_required(login_url="/")
def moyen(request):
	if request.method == "POST":
		if 'id' in request.POST and 'data' in request.POST:
			depense = get_object_or_404(Depense, pk=request.POST['id'])

			depense.moyen = request.POST['data']
			if is_gestionnaire_treso(get_object_or_404(Utilisateur, pk=request.user.pk), depense.association):
				depense.modifier = get_object_or_404(Utilisateur, pk=request.user.pk)
				depense.save()
	return HttpResponse(status=200, content_type="application/json")


@login_required(login_url="/")
def categorie(request):
	if request.method == "POST":
		if 'id' in request.POST and 'data' in request.POST:
			depense = get_object_or_404(Depense, pk=request.POST['id'])

			depense.categorie = request.POST['data']
			if is_gestionnaire_treso(get_object_or_404(Utilisateur, pk=request.user.pk), depense.association):
				depense.modifier = get_object_or_404(Utilisateur, pk=request.user.pk)
				depense.save()
	return HttpResponse(status=200, content_type="application/json")


@login_required(login_url="/")
def montant(request):
	if request.method == "POST":
		if 'id' in request.POST and 'data' in request.POST:
			depense = get_object_or_404(Depense, pk=request.POST['id'])

			depense.montant = request.POST['data']
			if is_gestionnaire_treso(get_object_or_404(Utilisateur, pk=request.user.pk), depense.association):
				depense.modifier = get_object_or_404(Utilisateur, pk=request.user.pk)
				depense.save()
	return HttpResponse(status=200, content_type="application/json")


@login_required(login_url="/")
def start_date(request):
	if request.method == "POST":
		if 'id' in request.POST and 'data' in request.POST:
			event = get_object_or_404(Evenement, pk=request.POST['id'])

			event.startDate = request.POST['data']
			event.save()
	return HttpResponse(status=200, content_type="application/json")


@login_required(login_url="/")
def end_date(request):
	if request.method == "POST":
		if 'id' in request.POST and 'data' in request.POST:
			event = get_object_or_404(Evenement, pk=request.POST['id'])

			event.endDate = request.POST['data']
			event.save()
	return HttpResponse(status=200, content_type="application/json")


@login_required(login_url="/")
def modify_date_event_ajax(request):
	if request.method == "POST" and request.session.has_key('association_user'):
		association = get_object_or_404(Association, nom=request.session['association_user'])
		event = get_object_or_404(Evenement, pk=request.POST['id'])
		event.startDate = request.POST['startDate']
		event.endDate = request.POST['endDate']

		if event.association == association:
			event.save()
	return HttpResponse(status=200, content_type="application/json")


@login_required(login_url="/")
def modify_event(request, association="", event=""):
	evenement = get_object_or_404(Evenement, pk=event)

	if request.method == 'POST':
		# Formular to modify the event picture
		if 'event_picture' in request.FILES:
			evenement.photo = request.FILES['event_picture']
			evenement.save()

		# Formular used to add content to the event description
		elif 'evenement_content' in request.POST and 'position_row' in request.POST and request.POST[
			'position_row'] != "":
			if 'modify_row' in request.POST:
				id = request.POST['modify_row']
				modified_row = get_object_or_404(RowDescription, pk=id)
				modified_row.delete()
			perform_formular_description(request, evenement)

		# Formular used to edit current description
		elif 'change_content' in request.POST:

			# Get the database object related to the content of the case that will be modified
			old_type = request.POST['old_type']
			if old_type == "img":
				old_content = get_object_or_404(ImageDescription, pk=request.POST['change_content'])
			else:
				old_content = get_object_or_404(TextDescription, pk=request.POST['change_content'])

			# Get the database object which contain the database object related to the modified case
			global_row = old_content.rowdescription_set.all()[0]

			# The new content is an image
			if 'img' in request.FILES:
				# Same than below
				if old_type == 'img':
					content = old_content
					content.image = request.FILES['img']
					content.save()
				else:
					global_row.texts.remove(old_content.pk)
					content = ImageDescription(image=request.FILES['img'], position=old_content.position)
					content.save()
					global_row.images.add(content.pk)
				content.save()

			# The new content is a text
			elif 'text' in request.POST and request.POST['text'] != "":
				# If it's the same type than before, it keeps the old object and just change the content
				if old_type == 'text':
					content = old_content
					content.text = request.POST['text']
					content.save()
				# If the type is different than before, it have to re-create another content object
				else:
					global_row.images.remove(old_content.pk)
					content = TextDescription(text=request.POST['text'], position=old_content.position)
					content.save()
					global_row.texts.add(content.pk)

			# The position of the block is changed
			elif 'position' in request.POST and request.POST['position'] != "":
				position_row = int(request.POST['position'])
				liste_description_row = RowDescription.objects.all().order_by('-position')
				if len(liste_description_row) > 0 and position_row <= liste_description_row[0].position:
					cursor = liste_description_row[0]
					i = 0
					while cursor.position != position_row:
						cursor.position += 1
						cursor.save()
						i += 1
						cursor = liste_description_row[i]
					cursor.position += 1
					cursor.save()
				elif len(liste_description_row) > 0:
					position_row = liste_description_row[0].position + 1

				old_content = old_content.rowdescription_set.all()[0]
				old_content.position = position_row
				old_content.save()

			# The css is modified
			if old_content in TextDescription.objects.all():
				content = old_content
				if 'fontsize' in request.POST and request.POST['fontsize'] != "":
					content.fontsize = int(request.POST['fontsize'])
				if 'fontalign' in request.POST and request.POST['fontsize'] != "NC":
					content.fontalign = request.POST['fontalign']
				if 'padding_top' in request.POST and request.POST['padding_top'] != "":
					content.padding_top = int(request.POST['padding_top'])
				if 'padding_bottom' in request.POST and request.POST['padding_bottom'] != "":
					content.padding_bottom = int(request.POST['padding_bottom'])
				if 'padding_left' in request.POST and request.POST['padding_left'] != "":
					content.padding_left = int(request.POST['padding_left'])
				if 'padding_right' in request.POST and request.POST['padding_right'] != "":
					content.padding_right = int(request.POST['padding_right'])
				content.save()

	row_descriptor_list = []  # Ensemble of description rows

	description = RowDescription.objects.none()
	try:
		description = evenement.row_descriptor.descriptions.all().order_by('position')
	except EvenementDescription.DoesNotExist:
		pass

	for row_descriptor in description:

		# Collects images and their respective position.
		# Store these images in the row_descriptor_sorted list

		# Store the offset of displaying
		disposition_case = row_descriptor.disposition_case
		nombre_element = len(row_descriptor.texts.all()) + len(row_descriptor.images.all())
		if disposition_case == 'centre':
			disposition_case = 1
		elif disposition_case == 'droite':
			if row_descriptor.fusion:
				disposition_case = 1
			else:
				disposition_case = 3 - nombre_element
		else:
			disposition_case = 0

		row_descriptor_sorted = ['', '', '']  # Represent a row of the description with it content sorted

		# Collect image and text then fill a list with these contents sorted from left to right
		for image in row_descriptor.images.all():
			position = position_to_index(image)
			row_descriptor_sorted[position] = image
		for text in row_descriptor.texts.order_by('pk'):
			position = position_to_index(text)
			row_descriptor_sorted[position] = text

		compteur = 0
		for elt in row_descriptor_sorted:
			if elt == "":
				compteur += 1

		# Store the current description row
		row_descriptor_list.append({
			'content': list(row_descriptor_sorted),
			'offset': disposition_case,
			'fusion': row_descriptor.fusion,
			'taille_fusion': row_descriptor.nombre_case * 4,
			'pk_row': row_descriptor.pk

		})

	print(row_descriptor_list)

	return render(request, 'cotisation/modifyEvent.html', {
		'evenement': evenement,
		'descriptions': row_descriptor_list,
		'fontalign': ['center', 'justify', 'left', 'right']
	})


def position_to_index(obj):
	"""
    Return the index related to the object position in the description grid
    :param obj: Define the content of the pointed grid case
    :return: index of the case
    """
	position = obj.position
	if position == 'gauche':
		position = 0
	elif position == 'centre':
		position = 1
	else:
		position = 2
	return position


def perform_formular_description(request, evenement):
	"""
    Process data send by the formular related to the description of the evenement.
    Collects formular's answers from the request.POST dictionnary and creates their
    related database objects.

    :param request: HttpRequest given by the modify_event function
    :param evenement: The event whose description will be changed
    :return: NONE
    """
	position_row = request.POST['position_row']

	taille_zone = request.POST['taille_zone']
	if 'case_disposition' in request.POST:
		case_disposition = request.POST['case_disposition']
	else:
		case_disposition = ''

	nombre_image = int(request.POST['nombre_image'])
	position_images = []
	images = []
	texts = []

	# Get images and their disposition from the formular
	for i in range(1, nombre_image + 1):
		if 'position_image_' + format(i) in request.POST:
			position_images.append(request.POST['position_image_' + format(i)])
			if 'image_' + format(i) in request.FILES:
				images.append(request.FILES['image_' + format(i)])

	# Get text from the formular
	i = 1

	while 'text_' + format(i) in request.POST:
		texts.append(request.POST['text_' + format(i)])
		i += 1

	# Creation of the database objects related to texts and images upload by the user
	i = 0
	image_descriptor = []
	text_descriptor = []
	position_taken = []
	for image in images:
		position_taken.append(position_images[i])
		new_image = ImageDescription(image=image, position=position_images[i])
		new_image.save()
		image_descriptor.append(new_image)
		i += 1

	for text in texts:
		position_possible = ['gauche', 'centre', 'droite']
		for elt in position_possible:
			if not (elt in position_taken):
				position = elt
				position_taken.append(elt)
				break
		new_text = TextDescription(text=text, position=position)
		new_text.save()
		text_descriptor.append(new_text)

	liste_description_row = RowDescription.objects.all().order_by('-position')
	if len(liste_description_row) > 0 and position_row <= liste_description_row[0].position:
		cursor = liste_description_row[0].position
		i = 0
		while cursor.position != position_row:
			cursor.position += 1
			cursor.save()
			i += 1
			cursor = liste_description_row[i]
		cursor.position += 1
		cursor.save()
	elif len(liste_description_row) > 0:
		position_row = liste_description_row[0].position + 1
	# Creation of the main database object used to store the new description of the event
	row_descriptor = RowDescription(
		nombre_case=taille_zone,
		disposition_case=case_disposition,
		fusion='fusion' in request.POST,
		position=position_row,
	)
	row_descriptor.save()

	for text in text_descriptor:
		row_descriptor.texts.add(text)
	for image in image_descriptor:
		row_descriptor.images.add(image)

	row_descriptor.save()

	# Add the main database object used to store the description into the global database
	# object used to store event information

	try:
		main_descriptor = EvenementDescription.objects.get(evenement=evenement)
	except EvenementDescription.DoesNotExist:
		# If the object doesn't exist it will be created
		main_descriptor = EvenementDescription(evenement=evenement)
		main_descriptor.save()

	main_descriptor.descriptions.add(row_descriptor)
	main_descriptor.save()


def delete_description_row(request):
	"""
    Ajax call to delete the row of description given through the POST dictionnary
    :param request:
    :return:
    """
	print("aaaaaaaaaaaaaaaaaaaa")
	if 'id' in request.POST:
		row = get_object_or_404(RowDescription, pk=request.POST['id'])
		for text in row.texts.all():
			text.delete()
		for image in row.images.all():
			image.delete()
		row.delete()
	return HttpResponse(status=200)
