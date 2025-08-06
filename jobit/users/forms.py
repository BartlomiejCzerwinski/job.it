from django import forms
from django.contrib.auth.forms import SetPasswordForm
from .models import AppUser
from .locations import LOCATIONS
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
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        label='Last Name',
        min_length=2,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        }),
        label='Password'
    )
    repeated_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repeat your password'
        }),
        label='Repeat Password'
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='Role',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Select your role'
        }),
        required=True
    )
    position = forms.CharField(
        label='Position',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your job position (e.g. Full Stack Developer)'
        })
    )
    country = forms.ChoiceField(
        label='Country',
        choices=[('', '---')] + [(country, country) for country in LOCATIONS.keys()],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Select your country'
        })
    )
    city = forms.ChoiceField(
        label='City',
        choices=[('', '---')],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Select your city'
        })
    )
    mobile = forms.CharField(
        label='Mobile',
        max_length=11,
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
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Select when you can start'
        })
    )
    is_remote = forms.BooleanField(
        label='Remote',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'title': 'Check if you are open to remote work'
        })
    )
    is_hybrid = forms.BooleanField(
        label='Hybrid',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'title': 'Check if you are open to hybrid work'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'country' in self.data:
            try:
                country = self.data.get('country')
                self.fields['city'].choices = [('', '---')] + [(city, city) for city in LOCATIONS.get(country, [])]
            except (ValueError, TypeError):
                pass
        elif 'initial' in kwargs and 'country' in kwargs['initial']:
            country = kwargs['initial']['country']
            self.fields['city'].choices = [('', '---')] + [(city, city) for city in LOCATIONS.get(country, [])]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        country = cleaned_data.get('country')
        city = cleaned_data.get('city')
        
        if role == 'worker':
            position = cleaned_data.get('position')
            starts_in = cleaned_data.get('starts_in')
            
            if not position:
                self.add_error('position', 'Position is required for workers')
            if not starts_in:
                self.add_error('starts_in', 'Start date is required for workers')
        
        if country and city:
            if city not in LOCATIONS.get(country, []):
                self.add_error('city', 'Please select a valid city for the chosen country')
        
        return cleaned_data


class PasswordResetForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your new password'
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your new password'
        }),
        strip=False,
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        return password2
