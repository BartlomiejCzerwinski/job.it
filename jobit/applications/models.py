from django.db import models
from users.models import AppUser
from jobs.models import JobListing

class Application(models.Model):
    job_listing = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    candidate = models.ForeignKey(AppUser, on_delete=models.CASCADE, null=True, blank=True)
    applied_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('ACCEPTED', 'Accepted'),
            ('REJECTED', 'Rejected')
        ],
        default='PENDING'
    )

    class Meta:
        unique_together = ['job_listing', 'candidate']
    
    def __str__(self):
        return f"Application for {self.job_listing.job_title} by {self.candidate}"
