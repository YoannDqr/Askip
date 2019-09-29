# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User

from django.forms import ModelForm

from datetime import date

# Create your models here.

class Association(models.Model):
    nom = models.CharField(max_length = 100, primary_key = True, unique = True)
    # Security of the password is let to a person in the association
    mdp = models.CharField(max_length = 1000)
    logo = models.ImageField(upload_to="upload/", blank = True, null = True)
    prix_cotisation = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    description = models.TextField(null=True, blank=True)
    module_tresorerie = models.BooleanField(default = True)
    module_club = models.BooleanField(default = True)
    module_vote = models.BooleanField(default=True)
    module_evenement = models.BooleanField(default=True)
    module_vente = models.BooleanField(default=True)

    def __str__(self):
        return self.nom + " " + self.prix_cotisation.__str__()

    def gestionnaire_mdp(self):
        p = Poste.objects.none()
        for poste in Poste.objects.filter(association=self):
            if poste.gestionnaire_mdp:
                p = p | Poste.objects.filter(pk=poste.pk)
        return p

    def gestionnaire_tresorerie(self):
        p = Poste.objects.none()
        for poste in Poste.objects.filter(association=self):
            if poste.gestionnaire_tresorerie:
                p = p | Poste.objects.filter(pk=poste.pk)
        print(p)
        return p


class Annee(models.Model):
    nom = models.CharField(max_length = 10)

    def __str__(self):
        return self.nom


class Utilisateur(User):
    photo = models.ImageField(upload_to="upload/", blank = True)
    date_naissance = models.DateField()
    adresse = models.CharField(max_length=1000) 
    annee = models.ForeignKey(Annee)

    def __str__(self):
        return self.username


class Poste(models.Model):
    titre = models.CharField(max_length = 100)
    association = models.ForeignKey(Association)
    personne = models.ManyToManyField(Utilisateur, related_name = "poste", blank=True)
    candidat = models.ManyToManyField(Utilisateur, related_name="poste_candidat", blank=True)
    description = models.TextField(blank=True)
    ca = models.BooleanField(default = False)
    gestionnaire_mdp = models.BooleanField(default = False)
    gestionnaire_tresorerie = models.BooleanField(default = False)
    reader_tresorerie = models.BooleanField(default = False)

    def __str__(self):
        return format(self.association) + " " + self.titre + " " + format(self.personne.all())

    def create_hierachie(self):
        hierarchie = Hierarchie(poste = self)
        hierarchie.save()


class Cotisation(models.Model):
    association = models.ForeignKey(Association, related_name = "cotisant")
    personne = models.ForeignKey(Utilisateur)
    stade = models.IntegerField(default = 0)
    
    def __str__(self):
        return format(self.association) + " " + format(self.personne) + " " + format(self.stade)
    
    def poste(self):
        p = Poste.objects.none()
        poste_dispo = self.personne.poste.all()
        for poste_plausible in poste_dispo:
            if poste_plausible.association == self.association:
                p = p|Poste.objects.filter(pk=poste_plausible.pk) #On somme que des queryset et pas des objets
        return p
        

class Club(models.Model):
    nom = models.CharField(max_length = 100, primary_key = True, unique = True)
    logo = models.ImageField(upload_to="upload/", blank = True, null = True)
    prix_cotisation = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    association = models.ForeignKey(Association, related_name="club")
    administrateurs = models.ManyToManyField(Cotisation)
    description = models.TextField()

    def __str__(self):
        return "Club " + self.nom + " de l'association " + self.association.nom


class Hierarchie(models.Model):
    poste = models.OneToOneField(Poste, related_name="poste", unique=True)
    fils = models.ManyToManyField(Poste, related_name="fils", blank=True)

    def __str__(self):
        return format(self.poste)


class Depense(models.Model):
    association = models.ForeignKey(Association)
    date = models.DateField(default = date.today)
    sujet = models.CharField(max_length=100, blank = True, null = True)
    commentaire = models.TextField(blank=True, null=True) 
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    categorie = models.CharField(max_length=100)
    moyen = models.CharField(max_length=100, blank=True, null=True)
    modifier = models.ForeignKey(Utilisateur, null=True, blank=True)

    def __str__(self):
        return format(self.association) + " " + self.sujet + " " + format(self.montant)


class Reponse(models.Model):
    reponse = models.TextField()
    nb_reponse = models.IntegerField(default = 0)

    def __str__(self):
        return self.reponse


class Vote(models.Model):
    association = models.ForeignKey(Association)
    accessibility = models.IntegerField(default = 0) # 0 = All; 1 = Prive; 2 = Restreint
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    question = models.TextField()
    reponse = models.ManyToManyField(Reponse)
    user_answered = models.ManyToManyField(Utilisateur)

    def __str__(self):
        return self.question
    
    def user(self):
        if self.accessibility == 0:
            return Utilisateur.objects.all()
        elif self.accessibility == 1:
            return Cotisant.objects.filter(association = self.association)
        elif self.accessibility == 2:
            users = Utilisateur.objects.none()
            postes = Poste.poste(self.association)

            for poste in postes:
                if poste.ca:
                    users = users | poste.personne.all()
            return users.distinct()


class Evenement(models.Model):
    nom = models.CharField(max_length=100)
    association = models.ForeignKey(Association, related_name="evenement")
    description = models.TextField(blank = True)
    photo = models.ImageField(upload_to="upload/", blank = True, null = True)
    startDate = models.DateTimeField(blank=True, null=True, unique=True)
    endDate = models.DateTimeField(blank=True, null=True, unique=True)
    prix = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    nombre_place = models.IntegerField(default = 0)
    cotisant = models.BooleanField(default = False)
    participant = models.ManyToManyField(Utilisateur, blank=True, related_name="evenementParticipe")
    candidat = models.ManyToManyField(Utilisateur, blank=True)

    def __str__(self):
        return self.nom + "   " + format(self.prix) + "E"

    def is_full(self):
        return len(self.participant.all()) >= self.nombre_place
    
    def can_participate(self, user):
        if not self.cotisant:
            return True
        else:
            for elt in self.association.cotisant:
                if elt.personne == user:
                    return True
            return False

    def add(self, user):
        if not self.is_full() or self.nombre_place == 0:
            self.participant.add(user)
            self.save()
            return True
        else:
            return False


class RowDescriptionException(Exception):
    def __init__(self, value):
        self.value = "RowDescriptionException raised : " + format(value)

    def __str__(self):
        return self.value


class ImageDescription(models.Model):
    image = models.ImageField(upload_to="upload/", blank=True, null=True)
    position = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return "Image en position : " + format(self.position)

    def save(self):
        if self.position in ['centre', 'gauche', 'droite']:
            super(ImageDescription, self).save()
        else:
            raise RowDescriptionException('The position of the image shall be nothing, centre, gauche or droite')


class TextDescription(models.Model):
    text = models.TextField()
    position = models.CharField(max_length=10, blank=True, null=True)
    fontsize = models.IntegerField(default=15)
    fontalign = models.CharField(default="left", max_length=10)
    padding_top = models.IntegerField(default=20)
    padding_bottom = models.IntegerField(default=20)
    padding_left = models.IntegerField(default=20)
    padding_right = models.IntegerField(default=20)

    def __str__(self):
        return format(self.text)

    def save(self):
        if self.position in ['centre', 'gauche', 'droite']:
            super(TextDescription, self).save()
        else:
            raise RowDescriptionException('The position of the text shall be nothing, centre, gauche or droite')


class RowDescription(models.Model):
    nombre_case = models.IntegerField(default=0)
    disposition_case = models.CharField(max_length=10, null=True, blank=True)
    images = models.ManyToManyField(ImageDescription, blank=True)
    texts = models.ManyToManyField(TextDescription, blank=True)
    fusion = models.BooleanField(default=False)
    position = models.IntegerField()

    def save(self, *args, **kwargs):
        if (
                int(self.nombre_case) <= 3 and
                (
                    self.disposition_case in ['', 'droite', 'gauche', 'centre'] or
                    not self.disposition_case
                )
        ):
            super(RowDescription, self).save(*args, **kwargs)
        else:
            raise RowDescriptionException('At least one parameter is not correct.')

    def delete(self):
        for text in self.texts.all():
            text.delete()
        for image in self.images.all():
            image.delete()

        position = self.position
        rows = RowDescription.objects.all().order_by('position')
        for row in rows:
            if row.position > position:
                row.position -= 1
                row.save()
        super(RowDescription, self).delete()


class EvenementDescription(models.Model):
    evenement = models.OneToOneField(Evenement, unique=True, related_name="row_descriptor")
    descriptions = models.ManyToManyField(RowDescription)

    def __str__(self):
        return "Evenement de l'association : " + format(self.evenement)
