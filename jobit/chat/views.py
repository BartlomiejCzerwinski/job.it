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
def init_conversation(request):
    """
    Initialize a conversation between two users for a specific job listing.
    Creates a new conversation if one doesn't exist, or returns existing conversation.
    Works for both recruiters and candidates.
    """
    try:
        data = json.loads(request.body)
        job_listing_id = data.get('job_listing_id')
        recipient_id = data.get('recipient_id')
        
        # Validate required fields
        if not all([job_listing_id, recipient_id]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields: job_listing_id, recipient_id'
            }, status=400)
        
        # Get the job listing
        job_listing = get_object_or_404(JobListing, id=job_listing_id)
        
        # Get the recipient user
        recipient_user = get_object_or_404(AppUser, id=recipient_id)
        
        # Get the current user
        current_user = request.user
        
        # Determine if current user is recruiter or candidate for this job listing
        is_recruiter = job_listing.owner.user == current_user
        
        if is_recruiter:
            # Current user is recruiter, recipient is candidate
            recruiter = current_user
            candidate = recipient_user.user
        else:
            # Current user is candidate, recipient is recruiter
            recruiter = recipient_user.user
            candidate = current_user
        
        # Check if conversation already exists
        conversation, created = Conversation.objects.get_or_create(
            job_listing=job_listing,
            recruiter=recruiter,
            candidate=candidate,
            defaults={
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            }
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Conversation initialized successfully',
            'data': {
                'conversation_id': conversation.id,
                'conversation_created': created,
                'sender_role': 'recruiter' if is_recruiter else 'candidate',
                'recipient_id': recipient_id,
                'job_listing_id': job_listing_id
            }
        }, status=201 if created else 200)
        
    except JobListing.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Job listing not found'
        }, status=404)
        
    except AppUser.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Recipient not found'
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
@require_http_methods(["POST"])
def send_message(request):
    """
    Send a message in an existing conversation.
    Requires conversation_id and content.
    """
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        content = data.get('content')
        
        # Validate required fields
        if not all([conversation_id, content]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields: conversation_id, content'
            }, status=400)
        
        # Get the conversation
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Verify user is part of this conversation
        current_user = request.user
        if current_user not in [conversation.recruiter, conversation.candidate]:
            return JsonResponse({
                'status': 'error',
                'message': 'You are not authorized to send messages in this conversation'
            }, status=403)
        
        # Create the message
        message = Message.objects.create(
            conversation=conversation,
            sender=current_user,
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
                'message_id': message.id,
                'conversation_id': conversation.id,
                'created_at': message.created_at.isoformat(),
                'sender_id': current_user.id
            }
        }, status=201)
        
    except Conversation.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Conversation not found'
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
                    'company': conversation.job_listing.company_name,
                    'location': str(conversation.job_listing.location) if conversation.job_listing.location else None,
                    'job_model': conversation.job_listing.job_model
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
                    'company': conversation.job_listing.company_name,
                    'location': str(conversation.job_listing.location) if conversation.job_listing.location else None,
                    'job_model': conversation.job_listing.job_model
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

@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """
    Get notification data for the current user (unread message count).
    """
    try:
        # Get user role to determine which conversations to check
        user_role = request.user.appuser.role
        
        total_unread = 0
        
        if user_role == 'recruiter':
            # Recruiter: check conversations where they are the recruiter
            conversations = Conversation.objects.filter(recruiter=request.user)
        elif user_role == 'worker':
            # Worker: check conversations where they are the candidate
            conversations = Conversation.objects.filter(candidate=request.user)
        
        # Count unread messages in relevant conversations
        for conversation in conversations:
            total_unread += conversation.get_unread_count(request.user)
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'unread_messages_count': total_unread,
                'has_unread_messages': total_unread > 0
            }
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_messages(request, conversation_id):
    """
    Get all messages for a specific conversation.
    """
    try:
        # Get the conversation
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Verify user is part of this conversation
        current_user = request.user
        if current_user not in [conversation.recruiter, conversation.candidate]:
            return JsonResponse({
                'status': 'error',
                'message': 'You are not authorized to view messages in this conversation'
            }, status=403)
        
        # Get all messages for this conversation
        messages = conversation.messages.all()
        
        # Serialize messages
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': message.id,
                'content': message.content,
                'sender_id': message.sender.id,
                'is_sent_by_me': message.sender == current_user,
                'created_at': message.created_at.isoformat(),
                'read_at': message.read_at.isoformat() if message.read_at else None
            })
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'conversation_id': conversation.id,
                'messages': messages_data
            }
        }, status=200)
        
    except Conversation.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Conversation not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def mark_conversation_read(request, conversation_id):
    """
    Mark all messages in a conversation as read for the current user.
    """
    try:
        # Get the conversation
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Verify user is part of this conversation
        current_user = request.user
        if current_user not in [conversation.recruiter, conversation.candidate]:
            return JsonResponse({
                'status': 'error',
                'message': 'You are not authorized to mark messages as read in this conversation'
            }, status=403)
        
        # Mark all unread messages as read
        unread_messages = conversation.messages.exclude(
            sender=current_user  # Messages from the other person
        ).filter(
            read_at__isnull=True
        )
        
        updated_count = unread_messages.update(read_at=timezone.now())
        
        return JsonResponse({
            'status': 'success',
            'message': f'Marked {updated_count} messages as read',
            'data': {
                'conversation_id': conversation.id,
                'messages_marked': updated_count
            }
        }, status=200)
        
    except Conversation.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Conversation not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)
