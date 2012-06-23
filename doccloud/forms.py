from django import forms
from doccloud.models import Document


class DocCloudDocForm(forms.ModelForm):
    class Meta:
        model = Document

    def save(self, force_insert=False, force_update=False, commit=True):
        import pdb;pdb.set_trace()