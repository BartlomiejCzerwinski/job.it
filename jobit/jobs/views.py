import json
import re

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_http_methods
from jobs.utils import get_listing_skills
from jobs.forms import JobListingForm
from users.models import Skill, UserSkill, AppUser, User, Location
from users.views import get_user_role, get_user, get_user_skills, get_profile_photo
from django.contrib.auth import logout
from users.views import get_user
from .models import JobListing, JobListingSkill
from applications.models import Application
from django.db.utils import IntegrityError
from users.locations import LOCATIONS
from applications.utils import get_job_listing_applications
ROLE_WORKER = "worker"
ROLE_RECRUITER = "recruiter"


@login_required
def index(request):
    role = get_user_role(request.user)
    if role == ROLE_WORKER:
        # Get regular job listings
        job_listings = get_all_listings()
        all_tiles = get_listings_tiles(job_listings, 4)

        # Filter remote offers only
        remote_job_listings = [job for job in job_listings if job.job_model == 'REMOTE']
        remote_tiles = get_listings_tiles(remote_job_listings, 4)
        
        # Get KNN matched jobs and convert to tiles
        knn_matched_jobs = get_knn_matches(request)
        knn_tiles = get_listings_tiles(knn_matched_jobs, 3)
        
        return render(request, 'jobs/index_worker.html', {
            "job_listings": all_tiles,
            "knn_matches": knn_tiles,
            "remote_offers": remote_tiles
        })
    elif role == ROLE_RECRUITER:
        # Get only active job listings for tiles
        active_listings = JobListing.objects.filter(status='ACTIVE')
        listings_tiles = get_listings_tiles(active_listings, 3)
        
        # Get all workers/candidates
        all_candidates = get_all_candidates()
        
        return render(request, 'jobs/index_recruiter.html', {
            "listings_tiles": listings_tiles,
            "candidates": all_candidates
        })


@login_required
def search_results_view(request):
    search_query = request.GET.get('q', '').strip()
    job_model = request.GET.get('model', '')
    salary_min = request.GET.get('salary_min')
    salary_max = request.GET.get('salary_max')
    currency = request.GET.get('currency', '')
    skills = request.GET.getlist('skills')  # Get list of skills from query params

    # Start with all job listings
    job_listings = JobListing.objects.all()

    # Apply search query filter
    if search_query:
        job_listings = job_listings.filter(
            job_title__icontains=search_query
        ) | job_listings.filter(
            company_name__icontains=search_query
        )

    # Apply job model filter
    if job_model:
        job_listings = job_listings.filter(job_model=job_model)

    # Apply salary range filter
    if salary_min:
        job_listings = job_listings.filter(salary_min__gte=salary_min)
    if salary_max:
        job_listings = job_listings.filter(salary_max__lte=salary_max)

    # Apply currency filter
    if currency:
        job_listings = job_listings.filter(salary_currency=currency)

    # Convert to list format for template and apply skill-based ranking
    job_list = []
    for job in job_listings:
        job_skills = get_listing_skills(job)
        job_skill_names = {skill['name'] for skill in job_skills}
        
        # Count how many requested skills this job has
        matching_skills = sum(1 for skill in skills if skill in job_skill_names)
        
        # Only include jobs that have at least one matching skill if skills were specified
        if not skills or matching_skills > 0:
            job_list.append({
                'id': job.id,
                'job_title': job.job_title,
                'job_location': str(job.location) if job.location else "",
                'company_name': job.company_name,
                'salary_min': job.salary_min,
                'salary_max': job.salary_max,
                'salary_currency': job.salary_currency,
                'skills': job_skills,
                'is_remote': job.job_model == 'REMOTE',
                'is_hybrid': job.job_model == 'HYBRID',
                'matching_skills_count': matching_skills  # Add this for sorting
            })

    # Sort jobs by number of matching skills (descending)
    if skills:  # Only sort by matching skills if skills were specified
        job_list.sort(key=lambda x: x['matching_skills_count'], reverse=True)

    return render(request, 'jobs/search_results.html', {
        'job_listings': job_list,
        'search_query': search_query,
        'filters': {
            'model': job_model,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'currency': currency,
            'skills': skills
        }
    })


@login_required
def worker_profile(request):
    user = request.user
    profile = get_user(request.user)
    location = getattr(profile, 'location', None)
    country = location.country if location else ""
    city = location.city if location else ""
    user_data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "position": getattr(profile, "position", ""),
        "location": str(location) if location else "",
        "country": country,
        "city": city,
        "is_remote": getattr(profile, "is_remote"),
        "is_hybrid": getattr(profile, "is_hybrid"),
        "mobile": getattr(profile, "mobile", ""),
        "starts_in": getattr(profile, "starts_in")
    }
    skills = get_user_skills(user)
    projects = profile.projects.all()  
    profile_photo_b64 = get_profile_photo(user.id)
    context = {
        "user_data": user_data,
        "locations_json": json.dumps(LOCATIONS),
        "skills": skills,
        "about_me": getattr(profile, "about_me", ""),
        "projects": projects,
        "profile_photo_b64": profile_photo_b64
    }
    return render(request, 'jobs/worker_profile.html', context)


@login_required
def listings_view(request):
    # Get filter parameter from URL, default to 'ACTIVE'
    status_filter = request.GET.get('status', 'ACTIVE')
    
    # Get all listings for the recruiter
    all_listings = get_recruiter_listings(request.user)
    
    # Filter by status
    if status_filter == 'ACTIVE':
        job_listings = all_listings.filter(status='ACTIVE')
    elif status_filter == 'CLOSED':
        job_listings = all_listings.filter(status='CLOSED')
    elif status_filter == 'ARCHIVED':
        job_listings = all_listings.filter(status='ARCHIVED')
    else:
        job_listings = all_listings.filter(status='ACTIVE')
    
    # Get counts for each status
    active_count = all_listings.filter(status='ACTIVE').count()
    closed_count = all_listings.filter(status='CLOSED').count()
    archived_count = all_listings.filter(status='ARCHIVED').count()
    
    num_of_listings = len(job_listings)
    is_successful_add_listing = request.GET.get('success')
    
    return render(request, 'jobs/listings.html',
                  {"job_listings": job_listings,
                   "is_success": is_successful_add_listing,
                   "num_of_listings": num_of_listings,
                   "current_filter": status_filter,
                   "active_count": active_count,
                   "closed_count": closed_count,
                   "archived_count": archived_count})


def listing_details_view(request, id):
    job_listing = get_object_or_404(JobListing, id=id)
    listing_skills = get_listing_skills(job_listing)
    user_role = get_user_role(request.user)
    
    has_applied = False
    if user_role == ROLE_WORKER:
        has_applied = Application.objects.filter(
            job_listing=job_listing, 
            candidate=get_user(request.user)
        ).exists()
    
    is_success = request.GET.get('success')
    
    # Add placeholder applications data for recruiters
    applications = []
    if user_role == ROLE_RECRUITER:
        applications = get_job_listing_applications(job_listing)
    
    return render(request, 'jobs/listing_details.html', {
        'job': job_listing, 
        'role': user_role, 
        'skills': listing_skills,
        'has_applied': has_applied,
        'is_success': is_success,
        'applications': applications
    })


@login_required
def add_listing_view(request):
    if request.method == "POST":
        form = JobListingForm(request.POST)
        if not form.is_valid():
            context = {
                "form": form,
                "locations_json": json.dumps(LOCATIONS),
            }
            return render(request, "jobs/add_listing.html", context)

        country = request.POST.get("country")
        city = request.POST.get("city")
        skills_string = request.POST.get("skillsListForListing")

        if not country or not city:
            form.add_error(None, "Please select both country and city")
            context = {
                "form": form,
                "locations_json": json.dumps(LOCATIONS),
            }
            return render(request, "jobs/add_listing.html", context)

        skills_data = parse_skills_from_form(skills_string)
        job_listing = form.save(commit=False)
        location, _ = Location.objects.get_or_create(country=country, city=city)
        job_listing.location = location
        job_listing.owner = get_user(request.user)
        job_listing.save()
        is_success = True
        if job_listing.owner is None:
            job_listing.delete()
            is_success = False

        query_string = '?success='
        print("is_success", is_success)
        if is_success:
            try:
                add_skills_to_job_listing(job_listing, skills_data)
                query_string += "True"
            except IntegrityError:
                query_string += "False"
        else:
            query_string += "False"

        return HttpResponseRedirect("/listings" + query_string)
    else:
        form = JobListingForm()

    context = {
        "form": form,
        "locations_json": json.dumps(LOCATIONS),
    }
    return render(request, "jobs/add_listing.html", context)


def parse_skills_from_form(skills_string):
    if skills_string:
        try:
            skills_data = json.loads(skills_string)
        except json.JSONDecodeError:
            skills_data = []
    else:
        skills_data = []
    return skills_data


def add_skills_to_job_listing(job_listing, skills):
    for skill in skills:
        print(skill)
        JobListingSkill.objects.create(job_listing=job_listing, skill=get_skill_by_id(skill['id']), level=skill['level'])


def get_all_candidates():
    """Get all workers/candidates with their skills and profile information"""
    candidates = AppUser.objects.filter(role='worker').select_related('user', 'location')
    data = []
    
    for candidate in candidates:
        user = candidate.user
        skills = candidate.userskill_set.select_related('skill').all()
        skills_data = sorted(
            [{'name': s.skill.name, 'level': s.level} for s in skills],
            key=lambda x: x['level'], reverse=True
        )
        
        data.append({
            'id': candidate.id,
            'name': f"{user.first_name} {user.last_name}",
            'position': candidate.position or "Not specified",
            'location': str(candidate.location) if candidate.location else "Not specified",
            'skills': skills_data,
            'profile_photo': get_profile_photo(candidate.id),
            'about_me': candidate.about_me or "No description available",
            'is_remote': candidate.is_remote,
            'is_hybrid': candidate.is_hybrid,
            'starts_in': candidate.starts_in or "Not specified"
        })
    
    return data


def get_recruiter_listings(email):
    recruiter = AppUser.objects.filter(user=email)[0]
    job_listings = JobListing.objects.filter(owner=recruiter)
    return job_listings


def get_listings_tiles(job_listings, number_of_skills_per_tile):
    result = []
    for job_listing in job_listings:
        skills = get_listing_skills(job_listing)[:number_of_skills_per_tile]
        # Count applications for this job listing
        applications_count = Application.objects.filter(job_listing=job_listing).count()
        result.append({
            "id": job_listing.id,
            "job_title": job_listing.job_title,
            "job_location": str(job_listing.location) if job_listing.location else "",
            "company_name": job_listing.company_name,
            "salary_min": job_listing.salary_min,
            "salary_max": job_listing.salary_max,
            "salary_currency": job_listing.salary_currency,
            "skills": skills,
            "is_remote": job_listing.job_model == 'REMOTE',
            "is_hybrid": job_listing.job_model == 'HYBRID',
            "status": job_listing.status,
            "applications_count": applications_count
        })
    return result


def get_all_listings():
    job_listings = JobListing.objects.all()
    return job_listings


def view_logout(request):
    logout(request)
    return HttpResponseRedirect('login')


def view_settings(request):
    return render(request, 'jobs/settings.html')


def get_skills(request):
    skills = Skill.objects.all().values("name", "id")
    return JsonResponse(list(skills), safe=False)


def get_skill_by_id(skill_id):
    return Skill.objects.filter(id=skill_id)[0]


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
            try:
                user_skill = UserSkill.objects.get(user=user, skill=skill)
                return JsonResponse({'error': 'Skill already defined for the user'}, status=400)
            except UserSkill.DoesNotExist:
                pass
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


@require_http_methods(["POST"])
def update_skill_level(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        skill_id = data.get('skillId')
        new_level = data.get('newLevel')

        user = get_user(request.user)

        if not all([skill_id, new_level]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        try:
            new_level = int(new_level)
            if new_level not in range(1, 4):
                return JsonResponse({'error': 'Skill level must be between 1 and 3'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Skill level must be an integer'}, status=400)

        try:
            skill = Skill.objects.get(id=skill_id)
            user_skill = UserSkill.objects.get(user=user, skill=skill)
            user_skill.level = new_level
            user_skill.save()
            return JsonResponse({'message': 'Skill level updated successfully'}, status=200)
        except Skill.DoesNotExist:
            return JsonResponse({'error': 'Skill does not exist'}, status=404)
        except UserSkill.DoesNotExist:
            return JsonResponse({'error': 'User does not have this skill'}, status=404)


@require_http_methods(["POST"])
def remove_skill(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        skill_id = data.get('id')

        user = get_user(request.user)

        if not skill_id:
            return JsonResponse({'error': 'Missing skill ID'}, status=400)

        try:
            skill = Skill.objects.get(id=skill_id)
            user_skill = UserSkill.objects.get(user=user, skill=skill)
            user_skill.delete()
            return JsonResponse({'message': 'Skill removed successfully'}, status=200)
        except Skill.DoesNotExist:
            return JsonResponse({'error': 'Skill does not exist'}, status=404)
        except UserSkill.DoesNotExist:
            return JsonResponse({'error': 'User does not have this skill'}, status=404)


@require_http_methods(["POST"])
def update_about_me(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        about_me = data.get('aboutMe')
        
        if about_me is None:
            return JsonResponse({'error': 'Missing about_me field'}, status=400)
            
        if len(about_me) > 250:
            return JsonResponse({'error': 'About Me text exceeds 250 characters'}, status=400)
            
        user = get_user(request.user)
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
            
        user.about_me = about_me
        user.save()
        
        return JsonResponse({'message': 'About Me updated successfully'}, status=200)


@login_required
@require_http_methods(["POST"])
def update_first_name(request):
    try:
        data = json.loads(request.body)
        first_name = data.get('first_name')
        
        if not first_name:
            return JsonResponse({'error': 'First name is required'}, status=400)
            
        user = request.user
        user.first_name = first_name
        user.save()
        
        return JsonResponse({'message': 'First name updated successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def update_last_name(request):
    try:
        data = json.loads(request.body)
        last_name = data.get('last_name')
        
        if not last_name:
            return JsonResponse({'error': 'Last name is required'}, status=400)
            
        user = request.user
        user.last_name = last_name
        user.save()
        
        return JsonResponse({'message': 'Last name updated successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def update_email(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)
            
        if not '@' in email or not '.' in email:
            return JsonResponse({'error': 'Invalid email format'}, status=400)
            
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            return JsonResponse({'error': 'Email is already taken'}, status=400)
            
        user = request.user
        user.email = email
        user.username = email
        user.save()
        
        return JsonResponse({'message': 'Email updated successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def update_mobile(request):
    try:
        data = json.loads(request.body)
        mobile = data.get('mobile')
        
        if not mobile:
            return JsonResponse({'error': 'Mobile number is required'}, status=400)
            
        # Validate mobile number format (xxx xxx xxx)
        if not re.match(r'^\d{3} \d{3} \d{3}$', mobile):
            return JsonResponse({'error': 'Phone number must be in format: xxx xxx xxx'}, status=400)
            
        user = get_user(request.user)
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
            
        user.mobile = mobile
        user.save()
        
        return JsonResponse({'message': 'Mobile number updated successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def update_starts_in(request):
    try:
        data = json.loads(request.body)
        starts_in = data.get('starts_in')
        
        if not starts_in:
            return JsonResponse({'error': 'Starts in value is required'}, status=400)
            
        valid_choices = ['ASAP', '2 weeks', '1 month', '3 months']
        if starts_in not in valid_choices:
            return JsonResponse({'error': 'Invalid starts in value'}, status=400)
            
        user = get_user(request.user)
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
            
        user.starts_in = starts_in
        user.save()
        
        return JsonResponse({'message': 'Starts in updated successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_knn_matches(request):
    from matching.views import knn_match
    response = knn_match(request)
    matches = json.loads(response.content)['matches']
    
    # Get job listings for matched jobs
    matched_jobs = []
    for match in matches:
        job = JobListing.objects.get(id=match['listing_id'])
        matched_jobs.append(job)
    print(matched_jobs)
    return matched_jobs


@login_required
@require_http_methods(["POST"])
def close_listing(request, listing_id):
    job_listing = get_object_or_404(JobListing, id=listing_id)
    user_role = get_user_role(request.user)
    
    if user_role != ROLE_RECRUITER:
        return JsonResponse({'error': 'Only recruiters can close job listings'}, status=403)
    
    if job_listing.owner != get_user(request.user):
        return JsonResponse({'error': 'You can only close your own job listings'}, status=403)
    
    if job_listing.status in ['CLOSED', 'ARCHIVED']:
        return JsonResponse({'error': f'Listing is already {job_listing.status.lower()}'}, status=400)
    
    try:
        job_listing.status = 'CLOSED'
        job_listing.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Job listing closed successfully',
            'listing_status': job_listing.status
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def archive_listing(request, listing_id):
    job_listing = get_object_or_404(JobListing, id=listing_id)
    user_role = get_user_role(request.user)
    
    if user_role != ROLE_RECRUITER:
        return JsonResponse({'error': 'Only recruiters can archive job listings'}, status=403)
    
    if job_listing.owner != get_user(request.user):
        return JsonResponse({'error': 'You can only archive your own job listings'}, status=403)
    
    if job_listing.status == 'ARCHIVED':
        return JsonResponse({'error': 'Listing is already archived'}, status=400)
    
    try:
        job_listing.status = 'ARCHIVED'
        job_listing.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Job listing archived successfully',
            'listing_status': job_listing.status
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def reactivate_listing(request, listing_id):
    job_listing = get_object_or_404(JobListing, id=listing_id)
    user_role = get_user_role(request.user)
    
    if user_role != ROLE_RECRUITER:
        return JsonResponse({'error': 'Only recruiters can reactivate job listings'}, status=403)
    
    if job_listing.owner != get_user(request.user):
        return JsonResponse({'error': 'You can only reactivate your own job listings'}, status=403)
    
    if job_listing.status == 'ACTIVE':
        return JsonResponse({'error': 'Listing is already active'}, status=400)
    
    if job_listing.status == 'ARCHIVED':
        return JsonResponse({'error': 'Archived listings cannot be reactivated'}, status=400)
    
    try:
        job_listing.status = 'ACTIVE'
        job_listing.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Job listing reactivated successfully',
            'listing_status': job_listing.status
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
