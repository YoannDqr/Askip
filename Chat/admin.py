from __future__ import unicode_literals

from django.contrib import admin

from .models import Message, Reponse, Pseudo


admin.site.register(Message)
admin.site.register(Reponse)
admin.site.register(Pseudo)
