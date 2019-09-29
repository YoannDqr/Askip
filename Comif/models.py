# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from Cotisation.models import Depense, Utilisateur, Association

from datetime import date, timedelta
# Create your models here.


class Client(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, null=True, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    solde = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    cotisant = models.BooleanField(default = False)
    association = models.ForeignKey(Association, blank=True, null=True)

    def is_solvable(self):
        return self.solde > -5


class Produit(models.Model):
    image = models.ImageField(upload_to = 'upload/', null=True, blank=True)
    nom = models.CharField(max_length=255, unique = True)
    prix = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    prix_achat = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    stock = models.IntegerField(default = 0)
    alerte_stock = models.IntegerField(default = 0)
    stock_faible = models.BooleanField(default = False)
    association = models.ForeignKey(Association, blank=True, null=True)

    def alert(self):
        return self.stock <= self.alerte_stock


class Categorie(models.Model):
    nom = models.CharField(max_length=255)
    produits = models.ManyToManyField(Produit, blank=True)
    association = models.ForeignKey(Association)


class Type(models.Model):
    nom = models.CharField(max_length=255, unique = True)
    categories = models.ManyToManyField(Categorie, blank=True)
    association = models.ForeignKey(Association)


class Achat(models.Model):
    description = models.TextField(blank=True, null = True)
    produits = models.ManyToManyField(Produit)
    utilisateur = models.ForeignKey(Client, related_name = 'achat')
    date = models.DateTimeField(auto_now=True)
    prix = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    association = models.ForeignKey(Association)

    def to_tresorerie(self):
        depense = Depense(
            association =   self.association,
            sujet       =   self.description,
            montant     =   self.prix,
            categorie   =   "Rechargement du compte"
        )
        depense.save()


class Commande(models.Model):
    produit = models.ForeignKey(Produit)
    quantite = models.IntegerField(default = 0)
    association = models.ForeignKey(Association)

    def __str__(self):
        return self.produit.nom + " * " + format(self.quantite)


class CommandeFinal(models.Model):
    produits = models.ManyToManyField(Commande, blank=True)
    date_envoie =  models.DateTimeField(auto_now=True)
    mail = models.EmailField(default="yoann.dequeker@etu.emse.fr")
    association = models.ForeignKey(Association)

    @staticmethod
    def next():
        last_commande = CommandeFinal.objects.filter(date_envoie__lte=date.today()).order_by("-date_envoie")
        if len(last_commande) > 0:
            last_date = last_commande[0].date_envoie
        else:
            last_date = date.today()
        return last_date + timedelta(7)

    def prix_total(self):
        prix = 0
        for produit in self.produits.all():
            prix += produit.produit.prix_achat * produit.quantite
        return prix 

    def __str__(self):
        return format(self.date_envoie) + " * " + format(self.prix_total())

