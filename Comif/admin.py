# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Client)
admin.site.register(Produit)
admin.site.register(Categorie)
admin.site.register(Achat)
admin.site.register(Type)
admin.site.register(Commande)
admin.site.register(CommandeFinal)