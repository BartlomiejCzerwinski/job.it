from django.db import models
from django.contrib.auth.models import User


class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about_me = models.TextField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_remote = models.BooleanField(default=False)
    is_hybrid = models.BooleanField(default=False)

    STARTS_IN_CHOICES = [
        ('ASAP', 'ASAP'),
        ('2 weeks', '2 weeks'),
        ('1 month', '1 month'),
        ('3 months', '3 months'),
    ]
    starts_in = models.CharField(
        max_length=50,
        choices=STARTS_IN_CHOICES,
        default='ASAP',
        blank=True,
        null=True
    )

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


class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)


class UserSkill(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.PositiveIntegerField()
