from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import AppUser


ROLE_WORKER = "worker"
ROLE_RECRUITER = "recruiter"


@login_required
def index(request):
    role = get_user_role(request.user)
    if role == ROLE_WORKER:
        return render(request, 'jobs/index_worker.html')
    elif role == ROLE_RECRUITER:
        return render(request, 'jobs/index_recruiter.html')


def get_user_role(email):
    role = AppUser.objects.filter(user=email).first().role
    return role
