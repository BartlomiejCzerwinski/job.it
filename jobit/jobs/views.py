import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from users.models import AppUser, Skill
from users.views import get_user_role, logout_user
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
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            skill_id = body.get("skillId")
            level = body.get("skillLevel")

            if not skill_id or not level:
                return JsonResponse({"error": "Both 'skillId' and 'skillLevel' are required"}, status=400)

            return JsonResponse({"message": f"Skill {skill_id} with level {level} added successfully"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
