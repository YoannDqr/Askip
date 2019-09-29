# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect

from django.utils import timezone

from .models import ReponseForm, MessageForm, Pseudo, Message, Reponse

from django.http import HttpResponse

from django.core.serializers import serialize

from django.contrib.auth.decorators import login_required

@login_required(login_url="/")
def index(request):

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = MessageForm(request.POST, request.FILES)
        form_reponse = ReponseForm(request.POST, request.FILES)
        post = dict(request.POST)
        # check whether it's valid:
        if (form.is_valid() or form_reponse.is_valid()) and post.has_key("pseudo") and post['pseudo'] != "" and (post.has_key("urls") or request.FILES.has_key("photo") or post.has_key("message")):
            
            if(len(Pseudo.objects.filter(nom = post['pseudo'])) > 0):
                pseudo = Pseudo.objects.filter(nom = post.pop('pseudo'))[0]
            else:
                pseudo = Pseudo(nom=post.pop('pseudo')[0])
                pseudo.save()
            if(post.has_key("type_comment") and post['type_comment'][0] == "Message"):
                try:
                    message = Message(user = pseudo, photo = request.FILES['photo'])
                except:
                    message = Message(user = pseudo)
                message = MessageForm(request.POST, instance=message)
                
                message = message.save()
                
            elif post.has_key("type_comment") and post['type_comment'][0] == "Reponse":
                try:
                    reponse = Reponse(user = pseudo, photo = request.FILES['photo'])
                except:
                    reponse = Reponse(user = pseudo)
                parent = Message.objects.get(pk = post['id_msg'][0])
                reponse.parent = parent
                reponse = ReponseForm(request.POST, instance=reponse)
                reponse = reponse.save()
                
            a = post['type_comment'][0]

    # if a GET (or any other method) we'll create a blank form
    else:
        form = MessageForm()
        form_reponse = ReponseForm()

    Chat = Message.objects.all().order_by('-date')

    return render(request, "chat/index.html", locals())

@login_required(login_url="/")
def rx(request):
    if request.method == 'POST':
        Messages = Message.objects.filter(pk__gt = request.POST['id'])
        for message in Messages:
            message.message = "<strong>"+ message.user.nom +"</strong><br>" + message.message + "<img src='" + message.url + "' alt=''><br><img src='/media/"+ str(message.photo) + "' alt=''><strong>" + str(message.date) + "</strong><br>" 

    return HttpResponse(serialize('json', Messages), status=200,content_type="application/json")