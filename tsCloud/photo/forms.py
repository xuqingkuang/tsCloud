from django import forms
from django.utils import simplejson

ACTION_CHOICES = (
    ('', 'None'),
    ('add', 'add'),
    ('change', 'change'),
    ('delete', 'delete'),
    ('test', 'test'),
)

TYPE_CHOICES = (
    ('json', 'json'),
    ('xml', 'xml'),
)

class UploadForm(forms.Form):
    data = forms.FileField()
    device_id = forms.CharField()
    model = forms.CharField()
    android_version = forms.CharField()
    phone_number = forms.CharField()

class RequestForm(forms.Form):
    a = forms.ChoiceField(choices=ACTION_CHOICES, required=False)
    p = forms.CharField()
    t = forms.ChoiceField(choices=TYPE_CHOICES, required=False)
    d = forms.FileField(required=False)

    def clean_p(self):
        return simplejson.loads(self.cleaned_data['p'])

