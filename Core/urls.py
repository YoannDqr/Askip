from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create_association/$', views.create_association, name='create_association'),
]