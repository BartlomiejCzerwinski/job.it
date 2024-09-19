from django.shortcuts import render, HttpResponse
from .forms import LoginForm

def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            # login...
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})