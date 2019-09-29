from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='chat.index'),
    url(r'^rx/$', views.rx, name='chat.rx'),

]