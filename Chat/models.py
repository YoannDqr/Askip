# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.forms import ModelForm, Textarea

from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


# Create your models here.

class Pseudo(models.Model):
    nom = models.CharField(max_length = 100, unique = True)


class Message(models.Model):
    user = models.ForeignKey(Pseudo)
    message = models.TextField(max_length=1000, blank = True)
    url = models.URLField(max_length = 1000, blank = True)
    photo = models.ImageField(upload_to="upload/", blank = True)
    date = models.DateTimeField(auto_now=True)

class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ('url', 'photo', 'message')

class Reponse(models.Model):
    parent = models.ForeignKey(Message, blank = False, null = False, related_name="messages", on_delete=models.CASCADE)
    user = models.ForeignKey(Pseudo, related_name="users")
    message = models.TextField(max_length=1000, blank = True)
    url = models.URLField(max_length = 1000, blank = True)
    photo = models.ImageField(upload_to="upload/", blank = True)
    date = models.DateTimeField(auto_now=True)

class ReponseForm(ModelForm):
    class Meta:
        model = Reponse
        fields = ('url', 'photo', 'message')
