from typing import List, Optional, Dict, Any
from django.db.models import Q
from .models import JobListing, JobListingSkill
from users.models import Skill, Location

def search_jobs(
    search_query: Optional[str] = None,
    job_model: Optional[str] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    currency: Optional[str] = None,
    skills: Optional[List[str]] = None,
    location: Optional[str] = None,
    company_name: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Search for jobs with multiple optional filters.
    
    Args:
        search_query (str, optional): Search in job title and company name
        job_model (str, optional): Filter by job model (REMOTE, HYBRID, ONSITE)
        salary_min (float, optional): Minimum salary
        salary_max (float, optional): Maximum salary
        currency (str, optional): Salary currency
        skills (List[str], optional): List of required skills
        location (str, optional): Job location
        company_name (str, optional): Company name
        limit (int, optional): Maximum number of results to return
        
    Returns:
        List[Dict[str, Any]]: List of job listings with their details
    """
    # Start with all job listings
    job_listings = JobListing.objects.all()

    # Apply search query filter
    if search_query:
        job_listings = job_listings.filter(
            Q(job_title__icontains=search_query) |
            Q(company_name__icontains=search_query)
        )

    # Apply job model filter
    if job_model:
        job_listings = job_listings.filter(job_model=job_model)

    # Apply salary range filter
    if salary_min is not None:
        job_listings = job_listings.filter(salary_min__gte=salary_min)
    if salary_max is not None:
        job_listings = job_listings.filter(salary_max__lte=salary_max)

    # Apply currency filter
    if currency:
        job_listings = job_listings.filter(salary_currency=currency)

    # Apply location filter
    if location:
        # Split location into country and city if possible
        location_parts = location.split(', ', 1)
        if len(location_parts) == 2:
            country, city = location_parts
            job_listings = job_listings.filter(
                Q(location__country__icontains=country) |
                Q(location__city__icontains=city)
            )
        else:
            job_listings = job_listings.filter(
                Q(location__country__icontains=location) |
                Q(location__city__icontains=location)
            )

    # Apply company name filter
    if company_name:
        job_listings = job_listings.filter(company_name__icontains=company_name)

    # Convert to list format and apply skill-based ranking
    job_list = []
    for job in job_listings:
        # Get job skills
        job_skills = JobListingSkill.objects.filter(job_listing=job)
        job_skill_names = {skill.skill.name for skill in job_skills}
        
        # Count matching skills if skills filter is applied
        matching_skills = 0
        if skills:
            matching_skills = sum(1 for skill in skills if skill in job_skill_names)
            # Skip jobs with no matching skills if skills filter is applied
            if matching_skills == 0:
                continue

        # Create job listing dictionary
        job_dict = {
            'id': job.id,
            'job_title': job.job_title,
            'job_location': str(job.location) if job.location else "",
            'company_name': job.company_name,
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'salary_currency': job.salary_currency,
            'job_model': job.job_model,
            'skills': [
                {
                    'name': skill.skill.name,
                    'level': skill.level
                } for skill in job_skills
            ],
            'is_remote': job.job_model == 'REMOTE',
            'is_hybrid': job.job_model == 'HYBRID',
            'matching_skills_count': matching_skills
        }
        job_list.append(job_dict)

    # Sort by matching skills count if skills filter is applied
    if skills:
        job_list.sort(key=lambda x: x['matching_skills_count'], reverse=True)

    # Apply limit if specified
    if limit is not None:
        job_list = job_list[:limit]

    return job_list 