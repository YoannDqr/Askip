from django.conf.urls import url, include
from . import views


urlpatterns = [

	url(r'^chat/get_conversation/$', views.Messages.as_view(), name='Api.getConversation'),

	url(r'^drive/permission/get_file/$', views.File.as_view(), name='Api.getFile'),
	url(r'^drive/permission/$', views.Permissions.as_view(), name='Api.drivePermission'),
	url(r'^drive/$', views.ManageDirectories.as_view(), name='Api.driveContent'),
	url(r'^newFile/$', views.File.as_view(), name='Api.newFile'),
	url(r'^users/$', views.Utilisateurs.as_view(), name='Api.users'),
]
