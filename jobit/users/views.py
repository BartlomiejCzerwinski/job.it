import json

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from users.models import AppUser, UserSkill, Skill
from .forms import LoginForm, RegisterForm
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/job.it')
            else:
                messages.error(request, "Wrong login data!")
                form = LoginForm()
                render(request, 'users/login.html', {'form': form})
    else:
        form = LoginForm()
    is_registration = request.GET.get('registration')
    if is_registration:
        messages.success(request, "Registration success!")
    return render(request, 'users/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name, last_name, email, password, repeated_password, role = extract_registration_form_data(form)
            if not is_password_valid(password, repeated_password):
                messages.error(request, "Wrong repeated password")
                form = RegisterForm()
                return render(request, 'users/register.html', {'form': form})

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already taken!")
                form = RegisterForm()
                return render(request, 'users/register.html', {'form': form})

            create_user(first_name, last_name, email, password, role)
            query_string = '?registration=ture'
            return HttpResponseRedirect('/job.it/login' + query_string)

    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def create_user(first_name, last_name, email, password, role):
    user = User.objects.create(username=email, first_name=first_name, last_name=last_name, email=email,
                               password=make_password(password))
    user.save()
    app_user = AppUser.objects.create(user=user, role=role)
    app_user.save()


def extract_registration_form_data(form):
    return form.cleaned_data.get('first_name'), \
        form.cleaned_data.get('last_name'), \
        form.cleaned_data.get('email'), \
        form.cleaned_data.get('password'), \
        form.cleaned_data.get('repeated_password'), \
        form.cleaned_data.get('role')


def is_password_valid(password, repeated_password):
    if password != repeated_password:
        return False
    return True


def get_current_user(request):
    user = request.user
    if user:
        return HttpResponse(user)
    return HttpResponse(None)


def get_user_skills(email):
    user = AppUser.objects.filter(user=email)[0]
    user_skills = UserSkill.objects.filter(user=user)
    skills = []
    for user_skill in user_skills:
        skills.append({"name": user_skill.skill.name, "level": user_skill.level, "id": user_skill.skill.id})
    return skills


@require_http_methods(["POST"])
def remove_skill(request):
    email = request.user
    data = json.loads(request.body)
    id = data.get("id")
    return remove_user_skill(email, id)


def get_user_role(email):
    role = AppUser.objects.filter(user=email).first().role
    return role


def get_user(email):
    user = AppUser.objects.filter(user=email).first()
    return user


def logout_user(request):
    logout(request)


def get_current_user_data(request):
    user = get_user(request.user)
    first_name = user.first_name
    last_name = user.last_name
    email = user.email
    user_data = {"firstName": first_name, "lastName": last_name, "email": email}
    return user_data


def remove_user_skill(email, skill_id):
    user = AppUser.objects.filter(user=email)[0]
    skill = Skill.objects.get(id=skill_id)

    if not user:
        return JsonResponse({'error': 'User does not exist'}, status=404)
    if not skill:
        return JsonResponse({'error': 'Skill does not exist'}, status=404)

    user_skill = UserSkill.objects.filter(user=user, skill=skill)[0]
    if not user_skill:
        return JsonResponse({'error': 'No such skill for the user'}, status=404)

    user_skill.delete()

    return JsonResponse({'message': 'Skill deleted successfully'}, status=201)
