from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

class Conversation(models.Model):
    job_listing = models.ForeignKey(
        'jobs.JobListing',
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recruiter_conversations'
    )
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='candidate_conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ['job_listing', 'recruiter', 'candidate']

    def __str__(self):
        return f"Conversation about {self.job_listing.title} - {self.candidate.username}"

    def get_last_message(self):
        return self.messages.order_by('-created_at').first()

    def get_unread_count(self, user):
        # Count messages sent by the other person that haven't been read
        other_user = self.candidate if user == self.recruiter else self.recruiter
        return self.messages.filter(
            sender=other_user,
            read_at__isnull=True
        ).count()

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message in {self.conversation}"

    def mark_as_read(self):
        """Mark the message as read."""
        if not self.read_at:
            self.read_at = timezone.now()
            self.save()

    @property
    def recipient(self):
        if self.sender == self.conversation.recruiter:
            return self.conversation.candidate
        return self.conversation.recruiter