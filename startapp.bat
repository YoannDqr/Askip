@echo off
IF "%1" =="" GOTO :no_parametre

py manage.py startapp %1
MD %1\static\css
MD %1\static\js
MD %1\static\img
MD %1\templates\%1

echo from django.conf.urls import url, include >> %1\urls.py
echo from . import views >> %1\urls.py
echo urlpatterns = [ >> %1\urls.py
echo url(r'^^$', views.index, name='%1.index'), >> %1\urls.py
echo ] >> %1\urls.py

echo. >> %1\static\css\%1.css
echo. >> %1\static\js\%1.js

echo {%%extends 'base.html'%%} >> %1\templates\%1\%1.html
echo {%%load static%%} >> %1\templates\%1\%1.html
echo. >> %1\templates\%1\%1.html
echo {%%block css%%}{%%endblock%%} >> %1\templates\%1\%1.html
echo. >> %1\templates\%1\%1.html
echo {%%block script%%}{%%endblock%%} >> %1\templates\%1\%1.html
echo. >> %1\templates\%1\%1.html
echo {%%block content%%}{%%endblock%%} >> %1\templates\%1\%1.html

goto :success

:no_parametre 
echo Un nom d'application est attendue
goto :fin

:success
echo L'application %1 a ete creee avec succes ! 
:fin
