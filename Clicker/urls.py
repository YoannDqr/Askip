from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='clicker.index'),
    url(r'^save/$', views.save, name='clicker.save'),
]



