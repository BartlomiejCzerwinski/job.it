import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse

from jobs.forms import JobListingForm
from users.models import Skill, UserSkill, AppUser
from users.views import get_user_role, get_user, get_user_skills
from django.contrib.auth import logout
from users.views import get_user
from .models import JobListing, JobListingSkill
from django.db.utils import IntegrityError
ROLE_WORKER = "worker"
ROLE_RECRUITER = "recruiter"


@login_required
def index(request):
    role = get_user_role(request.user)
    if role == ROLE_WORKER:
        job_listings = get_all_listings()
        return render(request, 'jobs/index_worker.html', {"job_listings": job_listings})
    elif role == ROLE_RECRUITER:
        return render(request, 'jobs/index_recruiter.html')


@login_required
def worker_profile(request):
    skills = get_user_skills(request.user)
    print(skills)
    return render(request, 'jobs/worker_profile.html', {'skills': skills})


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
    print(user_role)
    return render(request, 'jobs/listing_details.html', {'job': job_listing, 'role': user_role, 'skills': listing_skills})


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
