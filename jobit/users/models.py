from django.db import models
from django.contrib.auth.models import User


class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    RECRUITER = 'recruiter'
    WORKER = 'worker'
    ROLE_CHOICES = [
        (RECRUITER, 'Recruiter'),
        (WORKER, 'Worker'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=WORKER,
    )
