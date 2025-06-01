from django.shortcuts import render
from django.http import JsonResponse
from jobs.views import get_all_listings, get_listing_skills
from users.views import get_user_skills
from .vectorizer import JobMatchingVectorizer
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from openai import OpenAI
import json
import os
from typing import Dict, Any
from jobs.tools import search_jobs

def load_api_key():
    try:
        api_key_path = os.path.join(os.path.dirname(__file__), 'api_key.txt')
        with open(api_key_path, 'r') as file:
            api_key = file.read().strip()
            return api_key if api_key else None
    except (FileNotFoundError, IOError):
        return None


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

@csrf_exempt
@require_POST
def chat_endpoint(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '')
    except Exception:
        user_message = ''
        
    client = OpenAI(api_key=load_api_key())
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "system", "content": "You are AI assistant for Jobit. Your job it to help users find best jobs for them based on tools available to you. If user asks you for anything else, you should politely decline and say that you are not able to help with that."},
            {"role": "user", "content": user_message}
        ],
        tools=set_tools(),
        tool_choice="auto"
    )
    return JsonResponse({
        'reply': completion.choices[0].message.content
    })


def set_tools() -> Dict[str, Any]:
    """
    Returns a dictionary containing the function definitions for OpenAI function calling.
    """
    return {
    "name": "search_jobs",
    "description": "Search for jobs with multiple optional filters.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "search_query": {
                "type": "string",
                "description": "Search in job title and company name"
            },
            "job_model": {
                "type": "string",
                "description": "Filter by job model (REMOTE, HYBRID, ONSITE)"
            },
            "salary_min": {
                "type": "number",
                "description": "Minimum salary"
            },
            "salary_max": {
                "type": "number",
                "description": "Maximum salary"
            },
            "currency": {
                "type": "string",
                "description": "Salary currency"
            },
            "skills": {
                "type": "array",
                "description": "List of required skills",
                "items": {
                    "type": "string",
                    "description": "Required skill name"
                }
            },
            "location": {
                "type": "string",
                "description": "Job location"
            },
            "company_name": {
                "type": "string",
                "description": "Company name"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return"
            }
        },
        "additionalProperties": False,
        "required": [
            "search_query",
            "job_model",
            "salary_min",
            "salary_max",
            "currency",
            "skills",
            "location",
            "company_name",
            "limit"
        ]
    }
}
