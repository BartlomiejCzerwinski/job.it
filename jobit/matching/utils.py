from .vectorizer import JobMatchingVectorizer
from jobs.utils import get_listing_skills
from users.views import get_user_skills

def calculate_match_percentage(job_listing, candidate):
    """
    Returns the percentage match (0-100) between a job listing and a candidate (AppUser instance)
    using the same vectorizer logic as in knn_match, utilizing find_matches.
    """
    candidate_skills = get_user_skills(candidate.user)
    job_skills = get_listing_skills(job_listing)

    vectorizer = JobMatchingVectorizer(n_neighbors=1)
    candidate_vector = vectorizer.create_skill_vector(candidate_skills)
    job_vector = vectorizer.create_skill_vector(job_skills)

    matches = vectorizer.find_matches(candidate_vector, [{
        'listing_id': job_listing.id,
        'title': job_listing.job_title,
        'vector': job_vector
    }])
    if matches and matches[0]['listing_id'] == job_listing.id:
        percentage = int(round(matches[0]['match_score']))
    else:
        percentage = 0
    return percentage 