from .models import Application
from jobs.views import get_profile_photo

def get_job_listing_applications(job_listing):
    applications = Application.objects.filter(job_listing=job_listing).select_related('candidate__user')
    data = []
    for app in applications:
        candidate = app.candidate
        user = candidate.user
        skills = candidate.userskill_set.select_related('skill').all()
        skills_data = [{'name': s.skill.name, 'level': s.level} for s in skills]
        data.append({
            'id': app.id,
            'candidate_id': candidate.id,
            'name': f"{user.first_name} {user.last_name}",
            'position': candidate.position,
            'skills': skills_data,
            'status': app.status,
            'profile_photo': get_profile_photo(candidate.id)
        })
    return data 