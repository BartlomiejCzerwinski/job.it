from django.db import models

from users.models import AppUser


class JobListing(models.Model):
    CURRENCY_CHOICES = [
        ("PLN", "PLN"),
        ("EUR", "EUR"),
        ("USD", "USD"),
    ]

    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    about_company = models.TextField()
    job_description = models.TextField()
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="PLN")
    job_location = models.CharField(max_length=255)
    owner = models.ForeignKey(AppUser, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.job_title} at {self.company_name}"
