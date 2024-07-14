from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
    system_name = forms.CharField(max_length=255)
    version = forms.CharField(max_length=255)