import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Conversation, Message
from jobs.models import JobListing
from users.models import AppUser

# Create your views here.

@login_required
def index(request):
    return render(request, 'messages/index.html')

@login_required
@require_http_methods(["POST"])
def send_message(request):
    """
    Send a message to a candidate for a specific job listing.
    Creates a new conversation if one doesn't exist, or adds to existing conversation.
    """
    try:
        data = json.loads(request.body)
        job_listing_id = data.get('job_listing_id')
        candidate_id = data.get('candidate_id')
        content = data.get('content')
        
        # Validate required fields
        if not all([job_listing_id, candidate_id, content]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields: job_listing_id, candidate_id, content'
            }, status=400)
        
        # Get the job listing
        job_listing = get_object_or_404(JobListing, id=job_listing_id)
        
        # Get the candidate user
        candidate_user = get_object_or_404(AppUser, id=candidate_id)
        
        # Get the current user (recruiter)
        recruiter_user = get_object_or_404(AppUser, user=request.user)
        
        # Check if conversation already exists
        conversation, created = Conversation.objects.get_or_create(
            job_listing=job_listing,
            recruiter=recruiter_user.user,
            candidate=candidate_user.user,
            defaults={
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }
        )
        
        # Create the message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
            created_at=timezone.now()
        )
        
        # Update conversation's updated_at timestamp
        conversation.updated_at = timezone.now()
        conversation.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Message sent successfully',
            'data': {
                'conversation_id': conversation.id,
                'message_id': message.id,
                'created_at': message.created_at.isoformat(),
                'conversation_created': created
            }
        }, status=201)
        
    except JobListing.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Job listing not found'
        }, status=404)
        
    except AppUser.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Candidate not found'
        }, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_conversations(request):
    """
    Get all conversations for the current user (both as recruiter and candidate).
    """
    try:
        # Get conversations where user is recruiter
        recruiter_conversations = Conversation.objects.filter(recruiter=request.user)
        
        # Get conversations where user is candidate
        candidate_conversations = Conversation.objects.filter(candidate=request.user)
        
        # Combine and serialize conversations
        conversations_data = []
        
        for conversation in recruiter_conversations:
            last_message = conversation.get_last_message()
            conversations_data.append({
                'id': conversation.id,
                'job_listing': {
                    'id': conversation.job_listing.id,
                    'title': conversation.job_listing.job_title,
                    'company': conversation.job_listing.company_name
                },
                'other_user': {
                    'id': conversation.candidate.id,
                    'name': f"{conversation.candidate.first_name} {conversation.candidate.last_name}",
                    'position': getattr(conversation.candidate.appuser, 'position', ''),
                },
                'last_message': {
                    'content': last_message.content if last_message else '',
                    'created_at': last_message.created_at.isoformat() if last_message else None,
                    'sender_id': last_message.sender.id if last_message else None
                },
                'unread_count': conversation.get_unread_count(request.user),
                'updated_at': conversation.updated_at.isoformat(),
                'role': 'recruiter'
            })
        
        for conversation in candidate_conversations:
            last_message = conversation.get_last_message()
            conversations_data.append({
                'id': conversation.id,
                'job_listing': {
                    'id': conversation.job_listing.id,
                    'title': conversation.job_listing.job_title,
                    'company': conversation.job_listing.company_name
                },
                'other_user': {
                    'id': conversation.recruiter.id,
                    'name': f"{conversation.recruiter.first_name} {conversation.recruiter.last_name}",
                    'position': getattr(conversation.recruiter.appuser, 'position', ''),
                },
                'last_message': {
                    'content': last_message.content if last_message else '',
                    'created_at': last_message.created_at.isoformat() if last_message else None,
                    'sender_id': last_message.sender.id if last_message else None
                },
                'unread_count': conversation.get_unread_count(request.user),
                'updated_at': conversation.updated_at.isoformat(),
                'role': 'candidate'
            })
        
        # Sort by updated_at (most recent first)
        conversations_data.sort(key=lambda x: x['updated_at'], reverse=True)
        
        return JsonResponse({
            'status': 'success',
            'data': conversations_data
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)
