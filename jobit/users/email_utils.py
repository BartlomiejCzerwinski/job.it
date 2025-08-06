from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

def send_password_reset_email(user, reset_url):
    """
    Send password reset email to user
    """
    try:
        subject = 'Password Reset Request - Job.it'
        
        # Create context for the email template
        context = {
            'user_name': user.first_name or user.username,
            'reset_url': reset_url,
            'site_name': 'Job.it'
        }
        
        # Render HTML email
        html_message = render_to_string('users/emails/password_reset.html', context)
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False

def send_password_reset_success_email(user):
    """
    Send confirmation email when password is successfully reset
    """
    try:
        subject = 'Password Successfully Reset - Job.it'
        
        context = {
            'user_name': user.first_name or user.username,
            'site_name': 'Job.it',
            'site_url': 'http://127.0.0.1:8000/login'
        }
        
        html_message = render_to_string('users/emails/password_reset_success.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending password reset success email: {e}")
        return False

def generate_password_reset_url(user, request):
    """
    Generate password reset URL with token
    """
    # Generate token
    token = default_token_generator.make_token(user)
    
    # Encode user ID
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Build reset URL
    reset_url = request.build_absolute_uri(
        reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    )
    
    return reset_url 