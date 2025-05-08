from django import forms
from .models import AppUser
import re


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password')


def validate_phone_number(value):
    if value and not re.match(r'^\d{3} \d{3} \d{3}$', value):
        raise forms.ValidationError('Phone number must be in format: xxx xxx xxx')


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
        max_length=11,
        required=False,
        validators=[validate_phone_number],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'xxx xxx xxx',
            'pattern': r'\d{3} \d{3} \d{3}',
            'oninput': 'this.value = this.value.replace(/[^0-9]/g, "").replace(/(\d{3})(?=\d)/g, "$1 ").substring(0, 11)'
        })
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
