# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from Clicker.models import GameUser, LvlUser, Item

from django.http import HttpResponse

from django.core.serializers import serialize

from decimal import Decimal
# Create your views here.


def index(request):
    cookie = request.COOKIES
    
    if "game" in cookie.keys() and "pk" in cookie.keys() and "cle" in cookie.keys() and len(GameUser.objects.filter(pk=cookie['pk'], key=cookie['cle'])) >= 1 :
        #user = GameUser.objects.get(pk=cookie['pk'], key=cookie['cle'])
        user = GameUser.objects.filter(pk=cookie['pk'], key=cookie['cle'])[0]
    else:
        user = GameUser(key="12345")
        user.save()
        compteur = 0
        for item in Item.objects.all().order_by('premier'):
            if compteur < 10: #on ouvre que les 10 premiers objets

                if item.premier:
                    if len(LvlUser.objects.filter(item = item, niveau = 1)) == 1:
                        user.items.add(LvlUser.objects.get(item = item, niveau = 1))
                    else:
                        lvlUser = LvlUser(item=item, niveau=1)
                        lvlUser.save()
                        user.items.add(lvlUser)
                else:
                    if len(LvlUser.objects.filter(item = item, niveau = 0)) == 1:
                        user.items.add(LvlUser.objects.get(item = item, niveau = 0))
                    else:
                        lvlUser = LvlUser(item=item, niveau=0)
                        lvlUser.save()
                        user.items.add(lvlUser)
            compteur += 1
        user.save()
    
    for niveau in user.items.all():
        niveau.item.prix *= niveau.niveau
    first = Item.objects.filter(premier = True)[0]
    for elt in user.items.all():
        if elt.item.premier:
            first_niveau = elt.niveau
            first_pk = elt.pk
            
    cps = 0
    for elt in user.items.all():
        if not elt.item.premier:
            cps += elt.item.cps * elt.niveau
        
    reponseHttp = render(request, "clicker/index.html", locals())

    reponseHttp.set_cookie('pk', user.pk)
    reponseHttp.set_cookie('cle', user.key)
    reponseHttp.set_cookie('game', True)

    return reponseHttp


def prix(lvl):
    nb = lvl.item.prix * Decimal.from_float(float(lvl.niveau) * 1.8)
    nb = '%E' % nb.quantize(Decimal('10') ** (-2))
    return str(nb.split('E')[0].rstrip('0').rstrip('.') + 'E' + nb.split('E')[1])

def total(user):
    nb = Decimal.from_float(float(user.nombre_cookie))
    nb = '%E' % nb.quantize(Decimal('10') ** (-2))
    return str(nb.split('E')[0].rstrip('0').rstrip('.') + 'E' + nb.split('E')[1])

def save(request):
    cookie = request.COOKIES
    if(cookie.has_key('pk') and cookie.has_key('cle') and len(GameUser.objects.filter(pk=cookie['pk'], key=cookie['cle'])) > 0):
        user = GameUser.objects.filter(pk=cookie['pk'])[0]
        user.nombre_cookie = request.POST['total']
        
        user.cps = request.POST['cps']
        
        if(len(LvlUser.objects.filter(pk=request.POST['lvl'])) > 0):
            
            niveau_last = LvlUser.objects.filter(pk=request.POST['lvl'])[0]
            if(len(LvlUser.objects.filter(item=niveau_last.item, niveau = request.POST['niveau'])) > 0):
                lvl = LvlUser.objects.filter(item=niveau_last.item, niveau = request.POST['niveau'])[0]
            else:
                lvl = LvlUser(item=niveau_last.item, niveau = request.POST['niveau']) 
                lvl.save()    
            
            for elt in user.items.all():
                if elt.item == lvl.item and elt.niveau != lvl.niveau:
                    user.items.remove(elt)
            if(request.POST['niveau'] != niveau_last.niveau):
                user.items.add(lvl)
            if len(niveau_last.gameuser_set.all()) == 0:
                niveau_last.delete()
            user.save()
            return HttpResponse("["+prix(lvl)+","+ total(user)+"]", status=200,content_type="application/json")
        else:
            return HttpResponse(status=500,content_type="application/json")
