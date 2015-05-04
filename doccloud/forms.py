from django import forms
from doccloud.models import Document


class DocCloudDocForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = "__all__"
