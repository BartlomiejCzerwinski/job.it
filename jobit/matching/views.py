from django.shortcuts import render
from django.http import JsonResponse
from jobs.views import get_all_listings, get_listing_skills
from users.views import get_user_skills
from .vectorizer import JobMatchingVectorizer


def knn_match(request):
    listings = get_all_listings()
    user_skills = get_user_skills(request.user)
    vectorizer = JobMatchingVectorizer(n_neighbors=3)
    
    # Create normalized user skill vector
    user_vector = vectorizer.create_skill_vector(user_skills)
    
    # Create normalized job skill vectors
    job_vectors = []
    for listing in listings:
        job_skills = get_listing_skills(listing)
        job_vector = vectorizer.create_skill_vector(job_skills)
        job_vectors.append({
            'listing_id': listing.id,
            'title': listing.job_title,
            'vector': job_vector
        })
    
    # Find best matches using KNN
    matches = vectorizer.find_matches(user_vector, job_vectors)
    
    return JsonResponse({
        'matches': matches
    })
