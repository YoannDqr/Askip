from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='cotisation.index'),
    url(r'^modify/vote/(?P<association>.*)/(?P<vote>.*)/$', views.modify_vote, name='cotisation.modifyVote'),
    url(r'^modify/evennement/(?P<association>.*)/(?P<event>.*)/$', views.modify_event, name='cotisation.modifyEvent'),
    url(r'^modify/evennement/delete_description/$', views.delete_description_row, name='cotisation.delete_description'),
    url(r'^modify/action/(?P<association>.*)/$', views.action, name='cotisation.action'),
    url(r'^modify/(?P<association>.*)/(?P<cotisant>.*)/$', views.modify, name='cotisation.modify'),
    url(r'^club/(?P<association>.*)/(?P<club>.*)/$', views.modify_club, name='cotisation.modifyClub'),
    url(r'^reset/(?P<association>.*)/(?P<cotisant>.*)/$', views.reset, name='cotisation.reset'),
    url(r'^paye/(?P<association>.*)/(?P<cotisant>.*)/$', views.paye, name='cotisation.paye'),
    url(r'^genere/(?P<association>.*)/(?P<cotisant>.*)/$', views.generation, name='cotisation.generation'),
    url(r'^dashboard/(?P<association>.*)/$', views.dashboard, name='cotisation.dashboard'),
    url(r'^fiche/(?P<cotisant>.*)/$', views.fiche, name='cotisation.fiche-cotisation'),
    url(r'^hierarchie/(?P<association>.*)/$', views.hierarchie, name='cotisation.hierarchie'),
    url(r'^tresorerie/date/$', views.date, name='tresorerie.date'),
    url(r'^tresorerie/sujet/$', views.sujet, name='tresorerie.sujet'),
    url(r'^tresorerie/categorie/$', views.categorie, name='tresorerie.categorie'),
    url(r'^tresorerie/montant/$', views.montant, name='tresorerie.montant'),
    url(r'^tresorerie/moyen/$', views.moyen, name='tresorerie.moyen'),
    url(r'^event/startDate/$', views.start_date, name='cotisation.startDate'),
    url(r'^event/endDate/$', views.end_date, name='cotisation.endDate'),
    url(r'checkout/$', views.checkout, name='cotisation.checkout'),
    url(r'^modifyEventDate/$', views.modify_date_event_ajax, name='modifyEventDate'),
]
