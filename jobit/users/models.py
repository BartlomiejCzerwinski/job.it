from django.db import models
from django.contrib.auth.models import User


class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about_me = models.TextField(blank=True, null=True)

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
