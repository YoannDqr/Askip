from django import forms


class UserForm(forms.Form):
    url = forms.CharField(max_length=1000)
    message = forms.CharField(widget=forms.Textarea)
    image = forms.ImageFields(upload_to="upload/")

