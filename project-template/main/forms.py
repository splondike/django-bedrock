from django import forms


class DemoForm(forms.Form):
    body_field = forms.DateTimeField()
    default_field = forms.DateTimeField(required=False)
    path_field = forms.CharField()
    header_field = forms.CharField(required=False)
