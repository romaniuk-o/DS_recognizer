from django import forms

class AnalyzeForm(forms.Form):
    image = forms.ImageField()
