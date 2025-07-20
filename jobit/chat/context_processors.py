from .models import Conversation

def message_notifications(request):
    """
    Context processor that adds message notification data to all templates.
    Returns unread message count for the current user.
    """
    if request.user.is_authenticated:
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
            
            return {
                'unread_messages_count': total_unread,
                'has_unread_messages': total_unread > 0
            }
        except Exception:
            # If there's any error, return safe defaults
            return {
                'unread_messages_count': 0,
                'has_unread_messages': False
            }
    else:
        # For non-authenticated users, return empty data
        return {
            'unread_messages_count': 0,
            'has_unread_messages': False
        } 