import json

from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from users.models import AppUser, Skill, UserSkill
from users.views import get_user_role, logout_user, get_user
from django.contrib.auth import logout

ROLE_WORKER = "worker"
ROLE_RECRUITER = "recruiter"


@login_required
def index(request):
    role = get_user_role(request.user)
    if role == ROLE_WORKER:
        return render(request, 'jobs/index_worker.html')
    elif role == ROLE_RECRUITER:
        return render(request, 'jobs/index_recruiter.html')


def worker_profile(request):
    return render(request, 'jobs/worker_profile.html')


def view_logout(request):
    logout(request)
    return HttpResponseRedirect('/job.it/login')


def view_settings(request):
    return render(request, 'jobs/settings.html')


def get_skills(request):
    skills = Skill.objects.all().values("name", "id")
    return JsonResponse(list(skills), safe=False)


def add_skill(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        skill_id = data.get('skillId')
        skill_level = data.get('skillLevel')

        user = get_user(request.user)

        if not all([skill_id, skill_level]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        try:
            skill_level = int(skill_level)
            if skill_level not in range(1, 4):
                return JsonResponse({'error': 'Skill level must be between 1 and 3'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Skill level must be an integer'}, status=400)

        try:
            skill = Skill.objects.get(id=skill_id)
        except Skill.DoesNotExist:
            return JsonResponse({'error': 'Skill does not exist'}, status=404)

        UserSkill.objects.create(user=user, skill=skill, level=skill_level)

        return JsonResponse({'message': 'Skill added successfully'}, status=201)
