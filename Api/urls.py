from django.conf.urls import url, include 
from . import views

from rest_framework_jwt.views import *

urlpatterns = [ 
	url(r'^$', views.index, name='Api.index'),
	url(r'^user/$', views.Users.as_view(), name='Api.user'),
	url(r'^codypen/', include('Api.codypen_urls')),

	url(r'^products/$', views.Produits.as_view(), name='Api.products'),
	url(r'^types/$', views.Types.as_view(), name='Api.types'),
	url(r'^associations/$', views.Associations.as_view(), name='Api.associations'),
	url(r'^achat/$', views.Achats.as_view(), name='Api.achats'),
	url(r'^reload/$', views.Reload.as_view(), name='Api.reload'),
	url(r'^history/$', views.History.as_view(), name='Api.history'),
	url(r'^categories/$', views.Categories.as_view(), name='Api.categories'),
	url(r'^miss_categorie/$', views.CategoriesMiss.as_view(), name='Api.categoriesMiss'),

	url(r'^api-auth/', include('rest_framework.urls')),
	url(r'^api-token-auth/', obtain_jwt_token),
	url(r'^api-token-refresh/', refresh_jwt_token),
	url(r'^api-token-verify/', verify_jwt_token),
]
