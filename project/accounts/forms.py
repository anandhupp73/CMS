from django import forms
from django.contrib.auth import authenticate
from .models import User

ROLE_CHOICES = [
    ('ADMIN', 'Admin'),
    ('PM', 'Project Manager'),
    ('SUP', 'Supervisor'),
    ('CONT', 'Contractor'),
    ('ACC', 'Accountant'),
]

class RoleLoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        role = cleaned_data.get('role')

        user = authenticate(username=username, password=password)

        if not user:
            raise forms.ValidationError("Invalid username or password")
        if user.role != role:
            raise forms.ValidationError(f"User does not have the role: {role}")
        self.user = user
        return cleaned_data
