from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import (
    ModelForm,
    CharField,
    TextInput,
    PasswordInput,
    ImageField,
    FileInput,
)

class AnalyzeForm(forms.Form):
    image = forms.ImageField()


class SignUpForm(UserCreationForm):
    username = CharField(
        min_length=3, max_length=50, required=True, widget=TextInput()
    )
    password1 = CharField(max_length=50, required=True, widget=PasswordInput())
    password2 = CharField(max_length=50, required=True, widget=PasswordInput())

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
