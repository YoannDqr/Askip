from django.forms import ModelForm
from .models import *

class ProduitForm(ModelForm):
    class Meta:
        model = Produit
        exclude = ['stock_faible', 'association']

class UserForm(ModelForm):
    class Meta:
        model = Client
        exclude = ['utilisateur', 'association']