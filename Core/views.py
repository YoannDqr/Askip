# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import AssociationForm
from Cotisation.models import *


@login_required(login_url="/")
def create_association(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = AssociationForm(request.POST)
            if form.is_valid():
                association = form.save()
                president = Poste(association=association, titre="President", description="Président de l'association", ca=True, gestionnaire_mdp=True, gestionnaire_tresorerie=True, reader_tresorerie = True)
                president.save()
                president.create_hierachie()

        form = AssociationForm()
        return render(request, 'core/create_association.html', locals())
    else:
        return HttpResponse('Only super-user are accepted here')