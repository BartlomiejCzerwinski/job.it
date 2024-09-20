from django.shortcuts import render, HttpResponse
from .forms import LoginForm, RegisterForm
from django.contrib.auth.hashers import make_password
from django.contrib import messages


def index(request):
    return render(request, 'users/index.html')


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            # login...
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            repeated_password = form.cleaned_data.get('repeated_password')
            if not is_password_valid(password, repeated_password):
                messages.error(request, "Wrong repeated password")
                form = RegisterForm()
                return render(request, 'users/register.html', {'form': form})
            return HttpResponse("Success!!")
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def is_password_valid(password, repeated_password):
    if password != repeated_password:
        return False
    return True