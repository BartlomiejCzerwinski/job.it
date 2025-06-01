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
from typing import Dict, Any, List
from jobs.tools import search_jobs

SYSTEM_PROMPT = (
    "You are AI assistant for Jobit. "
    "Your job is to help users find best jobs for them based on tools available to you. "
    "You will try to complete the user's request in the best way possible without unnecessary enlarging the scope of the request."
    "If user asks you for anything else, you should politely decline and say that "
    "you are not able to help with that."
)

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

def format_simple_job_tile(job):
    """
    Returns a compact HTML tile for a job with only the most important information: title, salary, location, skills.
    """
    skills_html = " ".join(
        f"<span class='skill'>{skill['name']}</span>"
        for skill in job.get('skills', [])
    )
    return (
        f"<div class='job-tile compact-tile'>"
        f"<div class='tile-header'><span class='job-title'>{job.get('job_title', '')}</span></div>"
        f"<div class='tile-row'><span class='salary'>{job.get('salary_min', '')} - {job.get('salary_max', '')} {job.get('salary_currency', '')}</span></div>"
        f"<div class='tile-row'><span class='location'>{job.get('job_location', '')}</span></div>"
        f"<div class='tile-row skills'>{skills_html}</div>"
        f"</div>"
    )

@csrf_exempt
@require_POST
def chat_endpoint(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '')
    except Exception:
        user_message = ''
        
    client = OpenAI(api_key=load_api_key())
    
    # First API call to get the model's response
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        tools=set_tools(),
        tool_choice="auto"
    )
    
    response_message = completion.choices[0].message
    print("Response message: ", response_message)
    
    # Check if the model wants to call a function
    if response_message.tool_calls:
        # Get the function call details
        tool_call = response_message.tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        # Execute the function
        if function_name == "search_jobs":
            search_results = search_jobs(**function_args)
            tiles_html = "<div class='ai-tiles'>" + "".join([format_simple_job_tile(job) for job in search_results]) + "</div>"
            intro = "Here are some jobs you might like:"
            return JsonResponse({
                'intro': intro,
                'tiles_html': tiles_html
            })
    
    return JsonResponse({
        'reply': response_message.content
    })


def set_tools() -> List[Dict[str, Any]]:
    """
    Returns a list of function definitions for OpenAI function calling.
    """
    return [{
        "type": "function",
        "function": {
            "name": "search_jobs",
            "description": "Search for jobs with multiple optional filters.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": ["string", "null"],
                        "description": "Search in job title and company name"
                    },
                    "job_model": {
                        "type": ["string", "null"],
                        "description": "Filter by job model (REMOTE, HYBRID, ONSITE)"
                    },
                    "salary_min": {
                        "type": ["number", "null"],
                        "description": "Minimum salary"
                    },
                    "salary_max": {
                        "type": ["number", "null"],
                        "description": "Maximum salary"
                    },
                    "currency": {
                        "type": ["string", "null"],
                        "description": "Salary currency"
                    },
                    "skills": {
                        "type": ["array", "null"],
                        "description": "List of required skills",
                        "items": {
                            "type": "string",
                            "description": "Required skill name"
                        }
                    },
                    "location": {
                        "type": ["string", "null"],
                        "description": "Job location"
                    },
                    "company_name": {
                        "type": ["string", "null"],
                        "description": "Company name"
                    },
                    "limit": {
                        "type": ["integer", "null"],
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
    }]
