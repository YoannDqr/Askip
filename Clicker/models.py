# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class ImageLvl(models.Model):
    name = models.CharField(max_length = 100)
    image = models.ImageField(upload_to="upload/", blank=True)

class Item(models.Model):
    premier = models.BooleanField(default = False)
    name = models.CharField(max_length=100, blank=False, null=False)
    image = models.ImageField(upload_to="upload/", blank=True)
    niveau_max = models.IntegerField(default = 0)
    cps = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image_niveau = models.ManyToManyField(ImageLvl)

    def __str__(self):
        return self.name + " niveau max : " + str(self.niveau_max)

class LvlUser(models.Model):
    item = models.ForeignKey(Item)
    niveau = models.IntegerField()

    def __str__(self):
        return self.item.name + " niveau : " + str(self.niveau) + " / " + str(self.item.niveau_max)

class GameUser(models.Model):
    nombre_cookie = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    items = models.ManyToManyField(LvlUser, blank = True)
    key = models.DecimalField(max_digits=5, decimal_places=0, default=0)
    cps = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return str(self.pk) + "     " + str(self.nombre_cookie)
