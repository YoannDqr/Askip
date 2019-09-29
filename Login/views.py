# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect

from django.utils import timezone

from .models import UserForm

from django.contrib.auth.models import User


# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return redirect('chat.index', permanent=True)
    else:
        return redirect("/login/", permanent=True)
        

def signIn(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            request.session.set['username'] = "BOB"
            request.session.set_expiry(SESSION_EXPIRE_AT_BROWSER_CLOSE=True)
            
            return render(request, "login/thanks.html", locals())

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserForm()
    return render(request, "login/index.html", locals())


def logout(request):
    request.session.flush()
    request.session['actif'] = False
    request.session.save()

    return redirect('login.index', permanent = True)