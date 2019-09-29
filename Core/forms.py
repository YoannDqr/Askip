from django.forms import ModelForm
from Cotisation.models import Association

class AssociationForm(ModelForm):
    class Meta:
        model = Association
        exclude = []