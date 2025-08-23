from django.db import models
from django.conf import settings
from users.models import AppUser
from jobs.models import JobListing


class Match(models.Model):
    """
    Model to represent a match between a job listing and a candidate
    """
    job_listing = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    candidate = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['job_listing', 'candidate']
        ordering = ['-score', '-created_at']
    
    def __str__(self):
        return f"Match: {self.candidate.user.username} - {self.job_listing.job_title} ({self.score})"
