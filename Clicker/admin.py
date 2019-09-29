from __future__ import unicode_literals

from django.contrib import admin

from .models import Item, LvlUser, GameUser, ImageLvl


admin.site.register(Item)
admin.site.register(LvlUser)
admin.site.register(GameUser)
admin.site.register(ImageLvl)
