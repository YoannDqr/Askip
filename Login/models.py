# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User

from django.forms import ModelForm, Textarea

class UserModel(models.Model):
    tag = models.IntegerField(default = 0)
    user = models.OneToOneField(User)

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

# Create your models here.
