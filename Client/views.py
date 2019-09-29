# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect,get_object_or_404

from django.contrib.auth.decorators import login_required
from Cotisation.models import *
from datetime import date, timedelta
from Comif.models import Client

# Create your views here.


@login_required(login_url="/")
def index(request):
    user = get_object_or_404(Utilisateur, pk=request.user.pk)
    error = {}
    if request.method == 'POST':
        error = accept_formular(request, user, error)

    association_cotise = Cotisation.objects.filter(personne = user)
    comptes = Client.objects.filter(utilisateur = user)
    print(comptes)
    return render(request, 'client/client.html', locals())


def accept_formular(request, user, error):
    if request.FILES.has_key('photo'):
        user.photo = request.FILES['photo']
        
    if request.POST.has_key('pseudo') and request.POST['pseudo'] != "":
        users = Utilisateur.objects.filter(username = request.POST['pseudo'])
        if len(users) > 0 and users[0] != user:
            error['pseudo'] = "Ce pseudo est déjà utilisé"
        elif len(users) == 0:
            user.username = request.POST['pseudo']
    
    if request.POST.has_key('nom'):
        if request.POST['nom'] != "":
            user.last_name = request.POST['nom']
        else:
            error['nom'] = "Le nom est obligatoire"
    
    if request.POST.has_key('prenom'):
        if request.POST['prenom'] != "":
            user.first_name = request.POST['prenom']
        else:
            error['prenom'] = "Le prénom est obligatoire"
    
    if request.POST.has_key('dateNaissance'):
        if request.POST['dateNaissance'] != "":
            user.date_naissance = request.POST['dateNaissance']

    if request.POST.has_key('mail') and request.POST['mail'] != "":
        if "@etu.emse.fr" in request.POST['mail']:
            user.email = request.POST['mail']
        else:
            error['mail'] = "Veuillez donner votre adresse EMSE"

    if request.POST.has_key('adresse'):
        if request.POST['adresse'] != "":
            user.adresse = request.POST['adresse']
        else:
            error['adresse'] = "L'adresse est obligatoire"

    user.save()
    return error


@login_required(login_url="/")
def associations_client(request, association_vise=""):
    if association_vise != "": 
        association_visible = get_object_or_404(Association, pk=association_vise)
    else:
        association_visible = ""
    associations = Association.objects.all()
    user_association = []
    user_poste = []
    user = get_object_or_404(Utilisateur, pk=request.user.pk)
    for association in Cotisation.objects.filter(personne=user):
        user_association.append(association.association)
        for poste in association.poste():
            user_poste.append(poste.pk)
    return render(request, 'client/mes_associations.html', locals())


@login_required(login_url="/")
def paye_cotisation(request):
    user = get_object_or_404(Utilisateur, pk=request.user.pk)
    if request.method == 'POST' and request.POST.has_key("choix_asso"):
        prix_total = 0
        poste_candidat = []
        associations = []

        for cotisation in user.cotisation_set.all():
            for poste in Poste.objects.filter(association=cotisation.association):
                if user in poste.candidat.all():
                    poste.candidat.remove(user)
                    poste.save()

        for key, value in request.POST.items():
            print(key + "\n")
            if 'association' in key:
                association = get_object_or_404(Association, pk=value)
                if len(Cotisation.objects.filter(personne = user, association=association)) == 0:
                    prix_total += association.prix_cotisation
                    associations.append(association)
            elif 'poste' in key:
                poste = get_object_or_404(Poste, pk=value)
                poste_candidat.append(poste)
                if not user in poste.personne.all():
                    poste.candidat.add(user)
                    poste.save()
        if prix_total > 0:
            return render(request, 'client/paye_cotisation.html', locals())
        else:
            return redirect('client.mes_associations')
    else:
        return redirect('client.mes_associations')


@login_required(login_url="/")
def mes_evenement(request):
    user = get_object_or_404(Utilisateur, pk=request.user.pk)
    evenements = Evenement.objects.filter(startDate__gt=date.today()).order_by('startDate')
    for event in evenements:
        if event.is_full():
            evenements = evenements.exclude(event)
    return render(request, 'client/mes_evenement.html', locals())    


@login_required(login_url="/")
def paye_evenement(request):
    user = get_object_or_404(Utilisateur, pk=request.user.pk)
    if request.method == 'POST':
        prix_total_event = 0

        for event in Evenement.objects.filter(startDate__gt=date.today()).order_by('association'):
            if user in event.candidat.all():
                event.candidat.remove(user)
                event.save()
        for key, value in request.POST.items():
            if 'event' in key:
                event = get_object_or_404(Evenement, pk=value)
                if not event.is_full() and not user in event.participant.all():
                    event.candidat.add(user)
                    prix_total_event += event.prix
                    event.candidat.add(user)
                    event.save()
        if prix_total_event != 0:
            evenements = user.evenement_set.all()
            return render(request, 'client/paye_evenement.html', locals())
        else:
            return redirect('client.mes_evenement')
    else:
        return redirect('client.mes_evenement')
                

@login_required(login_url="/")
def mes_votes(request):
    user = get_object_or_404(Utilisateur, pk=request.user.pk)

    if request.method == "POST":
        for key, value in request.POST.items():
            if "vote_" in key and value != "NULL":
                pk = key.split('_')[1]
                vote = get_object_or_404(Vote, pk=pk)
                reponse = get_object_or_404(Reponse, pk=value)
                if reponse in vote.reponse.all() and user in vote.user():
                    reponse.nb_reponse += 1
                    vote.user_answered.add(user)
                    reponse.save()
                    vote.save()

    cotisations = Cotisation.objects.filter(personne=user)
    votes = Vote.objects.none()
    votes_finis = Vote.objects.none()

    for elt in cotisations:
        votes = votes | elt.association.vote_set.filter(endDate__gt=date.today()-timedelta(1))
        votes_finis = votes_finis | elt.association.vote_set.filter(endDate__lt=date.today()-timedelta(1))
        for vote in elt.association.vote_set.filter(endDate__gt=date.today()-timedelta(1)):
            if not (user in vote.user()) or (user in vote.user_answered.all()):
                votes = votes.exclude(pk=vote.pk)

        for vote in elt.association.vote_set.filter(endDate__lt=date.today()):
            if not (user in vote.user()):
                votes_finis = votes.exclude(pk=vote.pk)

        votes_finis.order_by('startDate')
        
    return render(request, 'client/mes_votes.html', locals())


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


def evenement_description(request, event=""):
    evenement = get_object_or_404(Evenement, pk=event)

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

    return render(request, 'client/descriptionEvent.html', {
        'evenement': evenement,
        'descriptions': row_descriptor_list,
    })

