from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.contrib.postgres.fields import ArrayField
import json


class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about_me = models.TextField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
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


class SocialLink(models.Model):
    PLATFORM_CHOICES = [
        ('website', 'Personal Website'),
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('gitlab', 'GitLab'),
        ('stackoverflow', 'Stack Overflow'),
        ('medium', 'Medium'),
        ('devto', 'Dev.to'),
        ('portfolio', 'Portfolio'),
        ('other', 'Other')
    ]

    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField()
    display_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.user.email}'s {self.platform} link"


class Project(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    technologies = models.TextField(null=True, blank=True)  # Store as JSON string
    github_link = models.URLField(blank=True, null=True, validators=[URLValidator()])
    demo_link = models.URLField(blank=True, null=True, validators=[URLValidator()])
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.user.user.email}'s project: {self.title}"

    def get_technologies(self):
        if not self.technologies:
            return []
        return json.loads(self.technologies)

    def set_technologies(self, tech_list):
        self.technologies = json.dumps(tech_list)
