from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from users.models import AppUser
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
