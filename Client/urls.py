from django.conf.urls import url, include 
from . import views 

urlpatterns = [ 
    url(r'^$', views.index, name='client.index'),
    url(r'^mes_evennement/description/(?P<event>.*)/$', views.evenement_description, name='client.evenement'),
    url(r'^mes_associations/(?P<association_vise>.*)/$', views.associations_client, name='client.mes_associations_vise'),
    url(r'^mes_associations/$', views.associations_client, name='client.mes_associations'), 
    url(r'^paye_cotisation/$', views.paye_cotisation, name='client.paye_cotisation'), 
    url(r'^mes_evenements/$', views.mes_evenement, name='client.mes_evenement'), 
    url(r'^mes_votes/$', views.mes_votes, name='client.mes_votes'), 
    url(r'^paye_evenements/$', views.paye_evenement, name='client.paye_evenement'), 
] 
