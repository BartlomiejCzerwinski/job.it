from django import forms
from .models import JobListing


class JobListingForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = [
            "job_title",
            "company_name",
            "about_company",
            "job_description",
            "salary_min",
            "salary_max",
            "salary_currency",
            "job_location",
        ]

    job_title = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Provide title of the position"})
    )
    company_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Name of your company"})
    )
    about_company = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Tell something about your company"})
    )
    job_description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Describe the position"})
    )
    salary_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "From", "min": "0"})
    )
    salary_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "To", "min": "0"})
    )
    salary_currency = forms.ChoiceField(
        choices=JobListing.CURRENCY_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    job_location = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off", "placeholder": "Type to search"})
    )
