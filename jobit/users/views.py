from django.shortcuts import render, HttpResponse
from .forms import LoginForm, RegisterForm


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
            # register ...
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})
