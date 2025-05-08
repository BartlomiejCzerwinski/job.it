from django import forms
from .models import AppUser


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password')


class RegisterForm(forms.Form):
    ROLE_CHOICES = [
        ('', '---'),
        ('recruiter', 'Recruiter'),
        ('worker', 'Worker'),
    ]

    first_name = forms.CharField(
        label='First Name',
        min_length=2,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Last Name',
        min_length=2,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Password'
    )
    repeated_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Repeat Password'
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='Role',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    position = forms.CharField(
        label='Position',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    location = forms.CharField(
        label='Location',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mobile = forms.CharField(
        label='Mobile',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    starts_in = forms.ChoiceField(
        choices=AppUser.STARTS_IN_CHOICES,
        label='Starts in',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_remote = forms.BooleanField(
        label='Remote',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_hybrid = forms.BooleanField(
        label='Hybrid',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
