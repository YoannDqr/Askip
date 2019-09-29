from django.conf.urls import url, include 
from . import views 

urlpatterns = [ 
    
    url(r'^$', views.index, name='comif.index'), 
    url(r'^gestion/$', views.gestion, name='comif.gestion'),
    url(r'^ajaxComptabilite/$', views.ajax_compta, name='comif.ajaxCompta'),
    url(r'^ajaxCommande/$', views.ajax_commande, name='comif.ajaxCommande'),
    url(r'^createCommande/$', views.create_commande, name='comif.createCommande'),
    url(r'^ajaxDeleteUser/$', views.ajax_delete_user, name='comif.ajaxDeleteUser'),
    url(r'^ajaxDeleteCommande/$', views.ajax_delete_commande_final, name='comif.ajaxDeleteCommande'),
    url(r'^newCommande/$', views.create_commande_final, name='comif.createCommandeFinal'),
    url(r'^gestion/(?P<onglet>.*)/$', views.gestion, name='comif.gestion'),

] 
