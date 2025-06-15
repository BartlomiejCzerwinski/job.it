from jobs.models import JobListingSkill

def get_listing_skills(job_listing):
    job_listing_skills = JobListingSkill.objects.filter(job_listing=job_listing)
    skills = []
    for job_listing_skill in job_listing_skills:
        skills.append({"name": job_listing_skill.skill.name, "level": job_listing_skill.level, "id": job_listing_skill.skill.id})

    def level(e):
        return e['level']
    skills.sort(key=level, reverse=True)

    return skills