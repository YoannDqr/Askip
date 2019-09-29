# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Utilisateur)
admin.site.register(Association)
admin.site.register(Poste)
admin.site.register(Annee)
admin.site.register(Cotisation)
admin.site.register(Hierarchie)
admin.site.register(Depense)
admin.site.register(Club)
admin.site.register(Vote)
admin.site.register(Reponse)
admin.site.register(Evenement)
admin.site.register(ImageDescription)
admin.site.register(TextDescription)
admin.site.register(RowDescription)
admin.site.register(EvenementDescription)
