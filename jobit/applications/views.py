from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from jobs.models import JobListing
from users.views import get_user_role, get_user
from .models import Application
from django.db.models import Case, When, Value, IntegerField

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

@login_required
def my_applications(request):
    user = get_user(request.user)
    applications = Application.objects.filter(candidate=user).select_related('job_listing').annotate(
        status_order=Case(
            When(status='ACCEPTED', then=Value(0)),
            When(status='PENDING', then=Value(1)),
            When(status='REJECTED', then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        )
    ).order_by('status_order')
    return render(request, 'applications/my_applications.html', {
        'applications': applications
    })

@login_required
@require_http_methods(["POST"])
def accept_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    user_role = get_user_role(request.user)
    
    if user_role != ROLE_RECRUITER:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if application.job_listing.status != 'ACTIVE':
        return JsonResponse({'error': 'Job listing is not active'}, status=400)
    
    try:
        application.status = 'ACCEPTED'
        application.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def reject_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    user_role = get_user_role(request.user)
    
    if user_role != ROLE_RECRUITER:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if application.job_listing.status != 'ACTIVE':
        return JsonResponse({'error': 'Job listing is not active'}, status=400)
    
    try:
        application.status = 'REJECTED'
        application.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def set_pending_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    user_role = get_user_role(request.user)
    
    if user_role != ROLE_RECRUITER:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if application.job_listing.status != 'ACTIVE':
        return JsonResponse({'error': 'Job listing is not active'}, status=400)
    
    try:
        application.status = 'PENDING'
        application.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

