import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_http_methods

from jobs.forms import JobListingForm
from users.models import Skill, UserSkill, AppUser
from users.views import get_user_role, get_user, get_user_skills
from django.contrib.auth import logout
from users.views import get_user
from .models import JobListing, JobListingSkill, Application
from django.db.utils import IntegrityError
ROLE_WORKER = "worker"
ROLE_RECRUITER = "recruiter"


@login_required
def index(request):
    role = get_user_role(request.user)
    if role == ROLE_WORKER:
        job_listings = get_all_listings_for_tiles(4)
        return render(request, 'jobs/index_worker.html', {"job_listings": job_listings})
    elif role == ROLE_RECRUITER:
        return render(request, 'jobs/index_recruiter.html')


@login_required
def worker_profile(request):
    skills = get_user_skills(request.user)
    user = get_user(request.user)
    about_me = user.about_me if user else ""
    return render(request, 'jobs/worker_profile.html', {
        'skills': skills,
        'about_me': about_me,
        'user': user
    })


@login_required
def listings_view(request):
    job_listings = get_recruiter_listings(request.user)
    num_of_listings = len(job_listings)
    is_successful_add_listing = request.GET.get('success')
    return render(request, 'jobs/listings.html',
                  {"job_listings": job_listings,
                   "is_success": is_successful_add_listing,
                   "num_of_listings": num_of_listings})


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
    
    return render(request, 'jobs/listing_details.html', {
        'job': job_listing, 
        'role': user_role, 
        'skills': listing_skills,
        'has_applied': has_applied,
        'is_success': is_success
    })


@login_required
def apply(request, id):
    job_listing = get_object_or_404(JobListing, id=id)
    user_role = get_user_role(request.user)
    
    if user_role != ROLE_WORKER:
        return redirect('listing_details', id=id)
    
    if job_listing.status != 'ACTIVE':
        return redirect('listing_details', id=id)
    
    existing_application = Application.objects.filter(job_listing=job_listing, candidate=get_user(request.user)).first()
    if existing_application:
        return redirect('listing_details', id=id)

    try:
        Application.objects.create(
            job_listing=job_listing,
            candidate=get_user(request.user)
        )
        return redirect(f'/listings/{id}?success=True')
    except Exception as e:
        return redirect(f'/listings/{id}?success=False')


@login_required
def add_listing_view(request):
    if request.method == "POST":
        form = JobListingForm(request.POST)
        skills_data = parse_skills_from_form(request.POST.get("skills_data"))
        print("Skills for job listing: ", skills_data)
        if form.is_valid():
            job_listing = form.save()
            job_listing.owner = get_user(request.user)
            job_listing.save()
            is_success = True
            if job_listing.owner is None:
                job_listing.delete()
                is_success = False

            query_string = '?success='
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

    return render(request, "jobs/add_listing.html", {"form": form})


def parse_skills_from_form(skills_string):
    if skills_string:
        try:
            skills_data = json.loads(skills_string)
        except json.JSONDecodeError:
            skills_data = []
    return skills_data


def add_skills_to_job_listing(job_listing, skills):
    for skill in skills:
        print(skill)
        JobListingSkill.objects.create(job_listing=job_listing, skill=get_skill_by_id(skill['id']), level=skill['level'])


def get_recruiter_listings(email):
    recruiter = AppUser.objects.filter(user=email)[0]
    job_listings = JobListing.objects.filter(owner=recruiter)
    return job_listings


def get_all_listings_for_tiles(number_of_skills_per_tile):
    job_listings = get_all_listings()
    result = []
    for job_listing in job_listings:
        skills = get_listing_skills(job_listing)[:number_of_skills_per_tile]
        result.append({
            "id": job_listing.id,
            "job_title": job_listing.job_title,
            "job_location": job_listing.job_location,
            "company_name": job_listing.company_name,
            "salary_min": job_listing.salary_min,
            "salary_max": job_listing.salary_max,
            "salary_currency": job_listing.salary_currency,
            "skills": skills,
            "is_remote": job_listing.job_model == 'REMOTE',
            "is_hybrid": job_listing.job_model == 'HYBRID'
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


def get_listing_skills(job_listing):
    job_listing_skills = JobListingSkill.objects.filter(job_listing=job_listing)
    skills = []
    for job_listing_skill in job_listing_skills:
        skills.append({"name": job_listing_skill.skill.name, "level": job_listing_skill.level, "id": job_listing_skill.skill.id})

    def level(e):
        return e['level']
    skills.sort(key=level, reverse=True)

    return skills


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
