from django.db import models

# Create your models here.


class User(models.Model):
    RECRUITER = 'recruiter'
    WORKER = 'worker'

    ROLE_CHOICES = [
        (RECRUITER, 'Recruiter'),
        (WORKER, 'Worker'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=500)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=WORKER,
    )
