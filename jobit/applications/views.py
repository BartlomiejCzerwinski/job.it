from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from jobs.models import JobListing
from users.views import get_user_role, get_user
from .models import Application

ROLE_WORKER = "worker"
ROLE_RECRUITER = "recruiter"

@login_required
def apply(request, job_id):
    job_listing = get_object_or_404(JobListing, id=job_id)
    user_role = get_user_role(request.user)
    
    if user_role != ROLE_WORKER:
        return redirect('listing_details', id=job_id)
    
    if job_listing.status != 'ACTIVE':
        return redirect('listing_details', id=job_id)
    
    existing_application = Application.objects.filter(
        job_listing=job_listing, 
        candidate=get_user(request.user)
    ).first()
    
    if existing_application:
        return redirect('listing_details', id=job_id)

    try:
        Application.objects.create(
            job_listing=job_listing,
            candidate=get_user(request.user)
        )
        return redirect(f'/listings/{job_id}?success=True')
    except Exception as e:
        return redirect(f'/listings/{job_id}?success=False')
