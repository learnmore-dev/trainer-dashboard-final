# core/forms.py   (or any app, e.g. accounts/forms.py)

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=150)
    last_name = forms.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
