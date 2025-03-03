import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from users.models import Skill, UserSkill, AppUser
from users.views import get_user_role, get_user, get_user_skills
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


@login_required
def worker_profile(request):
    skills = get_user_skills(request.user)
    print(skills)
    return render(request, 'jobs/worker_profile.html', {'skills': skills})


@login_required
def listings_view(request):
    skills = get_user_skills(request.user)
    print(skills)
    return render(request, 'jobs/listings.html')


def view_logout(request):
    logout(request)
    return HttpResponseRedirect('login')


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
        added_skill = {"name": skill.name, "level": skill_level, "id": skill_id}

        return JsonResponse({'message': 'Skill added successfully', 'skill': added_skill}, status=201)


def update_user_skill(email, skill_id, new_level):
    user = AppUser.objects.filter(user=email)[0]
    skill = Skill.objects.get(id=skill_id)

    if not user:
        return JsonResponse({'error': 'User does not exist'}, status=404)
    if not skill:
        return JsonResponse({'error': 'Skill does not exist'}, status=404)
    if new_level not in range(1, 4):
        return JsonResponse({'error': 'Skill level must be between 1 and 3'}, status=400)

    user_skill = UserSkill.objects.filter(user=user, skill=skill)[0]
    if not user_skill:
        return JsonResponse({'error': 'No such skill for the user'}, status=404)

    user_skill.level = new_level
    user_skill.save()

    return JsonResponse({'message': 'Skill updated successfully'}, status=201)
