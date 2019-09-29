# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, get_object_or_404
from django.core.serializers import serialize
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
import decimal

from .models import *
from Cotisation.models import Utilisateur

from .forms import *

########################################################################################################################

# Minimal balance needed to be able to buy something
limit = -5


def association_login_required(call_back_function):
    def association_login_requiered_decorator(request):
        test = False
        if 'association_user' in request.session:
            association = get_object_or_404(Association, pk=request.session['association_user'])
            if association.module_vente:
                test = True
        if not test:
            return redirect(reverse('cotisation.index'))
        return call_back_function(request)

    return association_login_requiered_decorator


@association_login_required
def index(request):
    """
    Display the selling interface of the selling module.
    All the requests are given in the POST dictionnary and are processed in this function.
    :param request: http request
    :return: Http response to comif.html
    """

    association = get_object_or_404(Association, pk=request.session['association_user'])
    if request.method == "POST":
        ################################################################################################################
        #                                                                                                              #
        #                               Begin formulars processing                                                     #
        #                               ==========================                                                     #
        #              - 'produit'      :   check users accounts to get their balance                  ;               #
        #              - 'modal'        :   the user add money to an account                           ;               #
        #              - 'cotisation'   :   the user change the contributor status                     ;               #
        #              - 'del_client'   :   delete the selected client                                 ;               #
        #                                                                                                              #
        ################################################################################################################

        if 'client' in request.POST:
            client = get_object_or_404(Client, pk=request.POST['client'])
            commande = Achat(utilisateur=client, description="", association=association)
            commande.save()
            prix_total = 0
            for key, value in request.POST.items():
                if 'produit' in key:
                    produit = get_object_or_404(Produit, pk=value)
                    client.solde -= produit.prix * int(request.POST['qte_' + value])
                    prix_total += produit.prix * int(request.POST['qte_' + value])
                    produit.stock -= int(request.POST['qte_' + value])
                    commande.produits.add(produit)
                    commande.description += produit.nom + ' x ' + request.POST['qte_' + value]
                    produit.save()
                    produit.stock_faible = produit.alert()
                    produit.save()
                    client.save()
                    commande.save()
            commande.prix = prix_total
            commande.save()

        elif 'modal' in request.POST:
            client = get_object_or_404(Client, pk=request.POST['modal'])
            if 'recharge' in request.POST and request.POST['recharge'] != "":
                client.solde += decimal.Decimal(request.POST['recharge'])
                achat_recharge = Achat(
                    description="Rechargement de " + format(request.POST['recharge']) + "€",
                    utilisateur=client,
                    prix=decimal.Decimal(request.POST['recharge']),
                    association=association
                )
                achat_recharge.save()
                achat_recharge.to_tresorerie()
            elif 'cotisation' in request.POST:
                client.cotisant = True
            else:
                client.cotisant = False
            client.save()

        elif 'del_client' in request.POST:
            client = get_object_or_404(Client, pk=request.POST['del_client'])
            client.delete()

        ################################################################################################################
        #                                                                                                              #
        #                               End formulars processing                                                       #
        #                               ==========================                                                     #
        #                                                                                                              #
        ################################################################################################################

    clients = Client.objects.filter(association=association)
    types = Type.objects.filter(association=association)
    alertes = Produit.objects.filter(stock_faible=True, association=association)

    for commande in CommandeFinal.objects.filter(date_envoie__gte=date.today(), association=association):
        tmp = alertes
        for produit in tmp:
            for produitCommande in commande.produits.all():
                if produit == produitCommande.produit:
                    alertes = alertes.exclude(pk=produit.pk)

    return render(request, 'comif/comif.html', {
        'is_alerte' :   len(alertes) > 0,   # Is there any alerts ?
        'alertes'   :   alertes,            # List of alerts
        'clients'   :   clients,            # List of clients
        'types'     :   types,              # List of products diplayed
    })


def create_commande(request):
    """
    The user want to add the products whith a low stock displayed in the notification pop-up.
    Check if a command had been already created. If it isn't, it will create a command.
    Check if a command had been already created. If it isn't, it will create a command.
    :param request: Http request
    :return: redirect : index()
    """

    association = get_object_or_404(Association, pk=request.session['association_user'])

    # Get the products with a low stock.
    alertes = Produit.objects.filter(stock_faible=True)
    if len(alertes) > 0:
        # Check if there is a possible command related to the user command.
        commande = CommandeFinal.objects.filter(
                                                    date_envoie__gte    =   date.today(),
                                                    association         =   association
                                                ).order_by('date_envoie')
        if len(commande) > 0:
            commande = commande[0]
        else:
            # If there isn't any command, one is created.
            commande = CommandeFinal(
                association=association,
                date_envoie=CommandeFinal.next(),
                mail="yoanndequeker@etu.emse.fr"
            )

        commande.save()

        for produit in commande.produits.all():
            # Products added to the command are deleted from the alerts products displayed in notifucation pop-up
            if produit in alertes:
                alertes = alertes.exclude(pk=produit.pk)

        for produit in alertes:

            ############################################################################################################
            #                                                                                                          #
            #   It tries to anticipate the amount of each command's product that shall be ordered.                     #
            #       - Looks in the last command of the product the amount ordered and apply the same in the current    #
            #         command; if there isn't any previous command, the amount is fixed to 10                          #
            #                                                                                                          #
            #         TODO : Add the possibility to ask to user the amount to put by default                           #
            #                                                                                                          #
            ############################################################################################################

            previous_commande = Commande.objects.filter(produit=produit, association=association).order_by('-pk')

            if len(previous_commande) > 0:
                previous_commande = previous_commande[0]
            else:
                previous_commande = Commande(produit=produit, quantite=10, association=association)
                previous_commande.save()
            # The amount found is added to the current command
            commande.produits.add(previous_commande)
        commande.save()

    return redirect('comif.index', permanent=True)


def gestion(request, onglet=""):
    # Active tab
    open_onglet = onglet
    association = get_object_or_404(Association, pk=request.session['association_user'])
    if request.method == "POST":

        ################################################################################################################
        #                                                                                                              #
        #                               Begin formulars processing                                                     #
        #                               ==========================                                                     #
        #              - 'delete_[type, categorie, produit]'      :   delete the specified element              ;      #
        #              - 'modal_[type, categorie, produit] '      :   modify the specified element              ;      #
        #              - 'new_[type, categorie, produit, user]'   :   add a new item to the specified element   ;      #
        #              - 'commande'                               :   add or modify command                     ;      #
        #                                                                                                              #
        ################################################################################################################

        if 'delete_type' in request.POST:
            type_produit = get_object_or_404(Type, pk=request.POST['delete_type'])
            type_produit.delete()

        elif 'modal_type' in request.POST:
            type_produit = get_object_or_404(Type, pk=request.POST['modal_type'])

            # Categories are selectable with checkbox. If the chekbox isn't checked, then the category isn't linked to #
            # the type. So, all cotegories are unlinked to the modified type and only whose checkbox is checked will   #
            # be linked to the type.                                                                                   #

            for categorie in type_produit.categories.all():
                type_produit.categories.remove(categorie)

            for key, value in request.POST.items():
                # Checked categories are added to the modified type
                if 'categorie' in key:
                    categorie = get_object_or_404(Categorie, pk=value)
                    type_produit.categories.add(categorie)
                    type_produit.save()
                if 'nom_type' in key:
                    type_produit.nom = value
                    type_produit.save()

        elif 'delete_categorie' in request.POST:
            categorie = get_object_or_404(Categorie, pk=request.POST['delete_categorie'])
            categorie.delete()

        elif 'modal_categorie' in request.POST:
            # For explanation look at 'modal_type' explanations
            categorie = get_object_or_404(Categorie, pk=request.POST['modal_categorie'])
            for elt in categorie.produits.all():
                categorie.produits.remove(elt)
            for key, value in request.POST.items():
                if 'produit' in key:
                    produit = get_object_or_404(Produit, pk=value)
                    categorie.produits.add(produit)
                    categorie.save()
                if 'nom_categorie' in key:
                    categorie.nom = value
                    categorie.save()

        elif (
            'new_type' in request.POST and
            'nom_type' in request.POST and
            request.POST['nom_type'] != ""
        ):
            type_produit = Type(nom=request.POST['nom_type'], association=association)
            type_produit.save()
            for key, value in request.POST.items():
                if 'categorie' in key:
                    categorie = get_object_or_404(Categorie, pk=value)
                    type_produit.categories.add(categorie)
            type_produit.save()

        elif (
                'new_categorie' in request.POST and
                'nom_categorie' in request.POST and
                request.POST['nom_categorie'] != ""
        ):
            categorie = Categorie(nom=request.POST['nom_categorie'], association=association)
            categorie.save()
            for key, value in request.POST.items():
                if 'produit' in key:
                    produit = get_object_or_404(Produit, pk=value)
                    categorie.produits.add(produit)
            categorie.save()

        elif 'delete_produit' in request.POST:
            produit = get_object_or_404(Produit, pk=request.POST['delete_produit'])
            produit.delete()

        elif 'modal_produit' in request.POST:
            form = ProduitForm(request.POST)
            produit = get_object_or_404(Produit, pk=request.POST['modal_produit'])
            save_produit = produit
            try:
                produit.delete()
                produit = form.save()
                produit.association = association
                if request.FILES.has_key('image'):
                    produit.image = request.FILES['image']

                produit.save()
            except:
                save_produit.save()

        elif 'new_produit' in request.POST:
            produit = Produit(
                                nom             =   request.POST['nom'],
                                prix            =   request.POST['prix'],
                                prix_achat      =   request.POST['prix_achat'],
                                stock           =   request.POST['stock'],
                                alerte_stock    =   request.POST['alerte_stock'],
                                association     =   association
                     )
            produit.save()
            if request.FILES.has_key('image'):
                produit.image = request.FILES['image']
            produit.save()

        elif 'new_user' in request.POST:
            if request.POST['user_id'] != 'NC':
                new_user = get_object_or_404(Utilisateur, pk=request.POST['user_id'])
                client = Client(
                                utilisateur =   new_user,
                                solde       =   request.POST['solde'],
                                association =   association,
                                cotisant    =   'cotisant' in request.POST)
            else:
                client = Client(
                                first_name  =   request.POST['first_name'],
                                last_name   =   request.POST['last_name'],
                                solde       =   request.POST['solde'],
                                cotisant    =   request.POST.has_key('cotisant'),
                                association =   association
                )
            client.save()

        elif 'commande_id' in request.POST:
            commande_final = get_object_or_404(CommandeFinal, pk=request.POST['commande_id'])
            for key, value in request.POST.items():
                if "produit_" in key:
                    produit = get_object_or_404(Produit, pk=value)
                    val = 'qte_' + value
                    if val in request.POST:
                        qte = int(request.POST['qte_' + value])
                        last_commande = commande_final.produits.all().filter(produit=produit)
                        if len(last_commande) > 0:
                            last_commande = last_commande[0]
                            qte += last_commande.quantite
                            commande_final.produits.remove(last_commande)
                            commande_final.save()

                            if len(last_commande.commandefinal_set.all()) == 0:
                                last_commande.delete()

                        commande = Commande.objects.filter(produit=produit, quantite=qte, association=association)
                        if len(commande) > 0:
                            commande = commande[0]
                        else:
                            commande = Commande(produit=produit, quantite=qte, association=association)
                            commande.save()
                        commande_final.produits.add(commande)
                        commande_final.save()

        ################################################################################################################
        #                                                                                                              #
        #                               End formulars processing                                                       #
        #                               ==========================                                                     #
        #                                                                                                              #
        ################################################################################################################

    types = Type.objects.filter(association=association)
    categories = Categorie.objects.filter(association=association)
    produits = Produit.objects.filter(association=association)
    produit_form = ProduitForm()
    user_form = UserForm()
    clients = Utilisateur.objects.all()

    for client in Client.objects.filter(association=association):
        if client.utilisateur is not None:
            clients = clients.exclude(pk=client.utilisateur.pk)

    usable_categories = categories
    usable_produit = produits
    for type_produit in types:
        for elt in type_produit.categories.filter(association=association):
            usable_categories = usable_categories.exclude(pk=elt.pk)

    for elt in categories:
        for produit in elt.produits.filter(association=association):
            usable_produit = usable_produit.exclude(pk=produit.pk)

    produit_modify_forms = {}
    for elt in produits:
        produit_modify_forms[elt.pk] = ProduitForm(
            initial={'nom': elt.nom, 'prix': elt.prix, 'prix_achat': elt.prix_achat, 'stock': elt.stock,
                     'alerte_stock': elt.alerte_stock})

    commandes = CommandeFinal.objects.filter(association=association)
    return render(request, 'comif/gestion.html', {
            'open_onglet'               :       open_onglet,                # Active tab
        
            'types'                     :       types,                      # List of all types
            'categories'                :       categories,                 # List of all categories
            'produits'                  :       produits,                   # List of all products
            'commandes'                 :       commandes,                  # List of all command created
            'clients'                   :       clients,                    # List of all clients
            'usableProduit'             :       usable_produit,             # Products not already linked to a category
            'usableCategorie'           :       usable_categories,          # Categories not already linked to a type
        
            'user_form'                 :       user_form,                  # Formular to add a new client
            'produit_form'              :       produit_form,               # Formular to create a new product
            'produit_modify_forms'      :       produit_modify_forms        # Formular to modify product : 1 per product
    })


def create_commande_final(request):
    association = get_object_or_404(Association, pk=request.session['association_user'])
    commande = CommandeFinal(association=association)
    commande.save()
    return redirect('comif.gestion', onglet='commande')


@require_http_methods(["POST"])
def ajax_compta(request):
    association = get_object_or_404(Association, pk=request.session['association_user'])
    if 'startDate' in request.POST and 'endDate' in request.POST:
        compta = Achat.objects.filter(
                                association =   association,
                                date__gte   =   request.POST['startDate'],
                                date__lte   =   request.POST['endDate']
        )

        return HttpResponse(serialize('json', compta), status=200, content_type="application/json")


@require_http_methods(["POST"])
def ajax_commande(request):
    if 'pk_commande' in request.POST and 'pk_produit' in request.POST:
        commande = get_object_or_404(CommandeFinal, pk=request.POST['pk_commande'])
        commande.produits.remove(get_object_or_404(Commande, pk=request.POST['pk_produit']))
        commande.save()
        return HttpResponse(status=200)


@require_http_methods(["POST"])
def ajax_delete_user(request):
    if 'pk' in request.POST:
        client = get_object_or_404(Client, pk=request.POST['pk'])
        client.delete()
        return HttpResponse(status=200)


@require_http_methods(["POST"])
def ajax_delete_commande_final(request):
    if 'pk_commande' in request.POST:
        commande = get_object_or_404(CommandeFinal, pk=request.POST['pk_commande'])
        commande.delete()
        return HttpResponse(status=200)
