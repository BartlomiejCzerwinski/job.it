import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from unittest.mock import patch, MagicMock
import json

from jobs.models import JobListing, JobListingSkill
from users.models import AppUser, Location, Skill
from jobs.forms import JobListingForm


class JobListingModelTest(TestCase):
    """Test JobListing model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
        self.location = Location.objects.create(
            country="Poland",
            city=f"Warsaw-{self.__class__.__name__}"
        )
        self.skill = Skill.objects.create(name="Python")
    
    def test_job_listing_creation(self):
        """Test creating a job listing"""
        job_listing = JobListing.objects.create(
            job_title="Software Engineer",
            company_name="Tech Corp",
            about_company="A great tech company",
            job_description="We are looking for a Python developer",
            salary_min=5000,
            salary_max=8000,
            salary_currency="PLN",
            location=self.location,
            job_model="REMOTE",
            owner=self.app_user,
            status="ACTIVE"
        )
        
        self.assertEqual(job_listing.job_title, "Software Engineer")
        self.assertEqual(job_listing.company_name, "Tech Corp")
        self.assertEqual(job_listing.about_company, "A great tech company")
        self.assertEqual(job_listing.job_description, "We are looking for a Python developer")
        self.assertEqual(job_listing.salary_min, 5000)
        self.assertEqual(job_listing.salary_max, 8000)
        self.assertEqual(job_listing.salary_currency, "PLN")
        self.assertEqual(job_listing.location, self.location)
        self.assertEqual(job_listing.job_model, "REMOTE")
        self.assertEqual(job_listing.owner, self.app_user)
        self.assertEqual(job_listing.status, "ACTIVE")
    
    def test_job_listing_default_values(self):
        """Test job listing default values"""
        job_listing = JobListing.objects.create(
            job_title="Developer",
            company_name="Company",
            about_company="About company",
            job_description="Job description"
        )
        
        self.assertEqual(job_listing.salary_currency, "PLN")
        self.assertEqual(job_listing.job_model, "STATIONARY")
        self.assertEqual(job_listing.status, "ACTIVE")
        self.assertIsNone(job_listing.salary_min)
        self.assertIsNone(job_listing.salary_max)
        self.assertIsNone(job_listing.location)
        self.assertIsNone(job_listing.owner)
    
    def test_job_listing_currency_choices(self):
        """Test job listing currency choices"""
        valid_currencies = ["PLN", "EUR", "USD"]
        
        for currency in valid_currencies:
            job_listing = JobListing.objects.create(
                job_title=f"Job {currency}",
                company_name="Company",
                about_company="About company",
                job_description="Job description",
                salary_currency=currency
            )
            self.assertEqual(job_listing.salary_currency, currency)
    
    def test_job_listing_job_model_choices(self):
        """Test job listing job model choices"""
        valid_models = ["STATIONARY", "HYBRID", "REMOTE"]
        
        for model in valid_models:
            job_listing = JobListing.objects.create(
                job_title=f"Job {model}",
                company_name="Company",
                about_company="About company",
                job_description="Job description",
                job_model=model
            )
            self.assertEqual(job_listing.job_model, model)
    
    def test_job_listing_status_choices(self):
        """Test job listing status choices"""
        valid_statuses = ["ACTIVE", "CLOSED", "ARCHIVED"]
        
        for status in valid_statuses:
            job_listing = JobListing.objects.create(
                job_title=f"Job {status}",
                company_name="Company",
                about_company="About company",
                job_description="Job description",
                status=status
            )
            self.assertEqual(job_listing.status, status)
    
    def test_job_listing_str_representation(self):
        """Test string representation of job listing"""
        job_listing = JobListing.objects.create(
            job_title="Python Developer",
            company_name="Tech Corp",
            about_company="About company",
            job_description="Job description"
        )
        
        expected_str = "Python Developer at Tech Corp"
        self.assertEqual(str(job_listing), expected_str)
    
    def test_job_listing_salary_validation(self):
        """Test job listing salary validation"""
        # salary_min should be less than or equal to salary_max
        job_listing = JobListing.objects.create(
            job_title="Developer",
            company_name="Company",
            about_company="About company",
            job_description="Job description",
            salary_min=5000,
            salary_max=8000
        )
        
        self.assertEqual(job_listing.salary_min, 5000)
        self.assertEqual(job_listing.salary_max, 8000)
        
        # salary_min can be equal to salary_max
        job_listing2 = JobListing.objects.create(
            job_title="Developer 2",
            company_name="Company",
            about_company="About company",
            job_description="Job description",
            salary_min=5000,
            salary_max=5000
        )
        
        self.assertEqual(job_listing2.salary_min, 5000)
        self.assertEqual(job_listing2.salary_max, 5000)


class JobListingSkillModelTest(TestCase):
    """Test JobListingSkill model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
        self.location = Location.objects.create(
            country="Poland",
            city=f"Warsaw-{self.__class__.__name__}"
        )
        self.skill = Skill.objects.create(name="Python")
        
        self.job_listing = JobListing.objects.create(
            job_title="Software Engineer",
            company_name="Tech Corp",
            about_company="About company",
            job_description="Job description"
        )
    
    def test_job_listing_skill_creation(self):
        """Test creating a job listing skill"""
        job_listing_skill = JobListingSkill.objects.create(
            job_listing=self.job_listing,
            skill=self.skill,
            level=5
        )
        
        self.assertEqual(job_listing_skill.job_listing, self.job_listing)
        self.assertEqual(job_listing_skill.skill, self.skill)
        self.assertEqual(job_listing_skill.level, 5)
    
    def test_job_listing_skill_unique_constraint(self):
        """Test that job listing-skill combination must be unique"""
        JobListingSkill.objects.create(
            job_listing=self.job_listing,
            skill=self.skill,
            level=5
        )
        
        # Should not be able to create another with same job_listing and skill
        with self.assertRaises(IntegrityError):
            JobListingSkill.objects.create(
                job_listing=self.job_listing,
                skill=self.skill,
                level=3
            )
    
    def test_job_listing_skill_level_validation(self):
        """Test job listing skill level validation"""
        # Level should be positive
        job_listing_skill = JobListingSkill.objects.create(
            job_listing=self.job_listing,
            skill=self.skill,
            level=1
        )
        self.assertEqual(job_listing_skill.level, 1)
        
        # Level can be 0 (beginner)
        job_listing_skill2 = JobListingSkill.objects.create(
            job_listing=self.job_listing,
            skill=Skill.objects.create(name="JavaScript"),
            level=0
        )
        self.assertEqual(job_listing_skill2.level, 0)


class JobViewsTest(TestCase):
    """Test job views functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
        self.location = Location.objects.create(
            country="Poland",
            city=f"Warsaw-{self.__class__.__name__}"
        )
        self.skill = Skill.objects.create(name="Python")
        
        self.job_listing = JobListing.objects.create(
            job_title="Software Engineer",
            company_name="Tech Corp",
            about_company="About company",
            job_description="Job description",
            owner=self.app_user
        )
    
    def test_job_listings_view(self):
        """Test job listings view"""
        response = self.client.get(reverse('job_listings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/listings.html')
    
    def test_job_listing_details_view(self):
        """Test job listing details view"""
        response = self.client.get(
            reverse('listing_details', kwargs={'listing_id': self.job_listing.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/listing_details.html')
        self.assertContains(response, "Software Engineer")
        self.assertContains(response, "Tech Corp")
    
    def test_job_listing_details_view_not_found(self):
        """Test job listing details view with non-existent listing"""
        response = self.client.get(
            reverse('listing_details', kwargs={'listing_id': 99999})
        )
        self.assertEqual(response.status_code, 404)
    
    def test_add_listing_view_get_authenticated(self):
        """Test add listing view GET request for authenticated user"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('add_listing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/add_listing.html')
    
    def test_add_listing_view_get_unauthenticated(self):
        """Test add listing view GET request for unauthenticated user"""
        response = self.client.get(reverse('add_listing'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_add_listing_view_post_success(self):
        """Test successful job listing creation"""
        self.client.force_login(self.user)
        
        data = {
            'job_title': 'New Job',
            'company_name': 'New Company',
            'about_company': 'About new company',
            'job_description': 'New job description',
            'salary_min': 6000,
            'salary_max': 9000,
            'salary_currency': 'PLN',
            'job_model': 'HYBRID',
            'status': 'ACTIVE'
        }
        
        response = self.client.post(reverse('add_listing'), data)
        
        # Should redirect after success
        self.assertEqual(response.status_code, 302)
        
        # Check if job listing was created
        self.assertTrue(JobListing.objects.filter(job_title='New Job').exists())
    
    def test_search_results_view(self):
        """Test search results view"""
        response = self.client.get(reverse('search_results'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/search_results.html')
    
    def test_search_results_view_with_query(self):
        """Test search results view with search query"""
        response = self.client.get(reverse('search_results'), {'q': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/search_results.html')
    
    def test_worker_profile_view(self):
        """Test worker profile view"""
        response = self.client.get(reverse('worker_profile'))
        # Should redirect to login for unauthenticated users
        self.assertEqual(response.status_code, 302)
    
    def test_worker_profile_view_authenticated(self):
        """Test worker profile view for authenticated user"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('worker_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs/worker_profile.html')


class JobFormsTest(TestCase):
    """Test job forms functionality"""
    
    def test_job_listing_form_valid(self):
        """Test valid job listing form"""
        form_data = {
            'job_title': 'Software Engineer',
            'company_name': 'Tech Corp',
            'about_company': 'About company',
            'job_description': 'Job description',
            'salary_min': 5000,
            'salary_max': 8000,
            'salary_currency': 'PLN',
            'job_model': 'REMOTE',
            'status': 'ACTIVE'
        }
        
        form = JobListingForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_job_listing_form_missing_required_fields(self):
        """Test job listing form with missing required fields"""
        form_data = {
            'company_name': 'Tech Corp',
            'about_company': 'About company'
            # Missing job_title and job_description
        }
        
        form = JobListingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('job_title', form.errors)
        self.assertIn('job_description', form.errors)
    
    def test_job_listing_form_salary_validation(self):
        """Test job listing form salary validation"""
        # salary_min greater than salary_max should be invalid
        form_data = {
            'job_title': 'Software Engineer',
            'company_name': 'Tech Corp',
            'about_company': 'About company',
            'job_description': 'Job description',
            'salary_min': 10000,
            'salary_max': 5000,  # Less than salary_min
            'salary_currency': 'PLN',
            'job_model': 'REMOTE',
            'status': 'ACTIVE'
        }
        
        form = JobListingForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Form should have validation error for salary fields


class JobUtilsTest(TestCase):
    """Test job utility functions"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
        self.location = Location.objects.create(
            country="Poland",
            city=f"Warsaw-{self.__class__.__name__}"
        )
        self.skill = Skill.objects.create(name="Python")
    
    def test_job_listing_with_skills(self):
        """Test job listing with associated skills"""
        job_listing = JobListing.objects.create(
            job_title="Python Developer",
            company_name="Tech Corp",
            about_company="About company",
            job_description="Job description"
        )
        
        # Add skills to job listing
        JobListingSkill.objects.create(
            job_listing=job_listing,
            skill=self.skill,
            level=5
        )
        
        # Check if skill is associated
        self.assertEqual(job_listing.joblistingskill_set.count(), 1)
        self.assertEqual(job_listing.joblistingskill_set.first().skill, self.skill)
        self.assertEqual(job_listing.joblistingskill_set.first().level, 5)
    
    def test_job_listing_filtering_by_status(self):
        """Test filtering job listings by status"""
        # Create job listings with different statuses
        active_job = JobListing.objects.create(
            job_title="Active Job",
            company_name="Company",
            about_company="About company",
            job_description="Job description",
            status="ACTIVE"
        )
        
        closed_job = JobListing.objects.create(
            job_title="Closed Job",
            company_name="Company",
            about_company="About company",
            job_description="Job description",
            status="CLOSED"
        )
        
        # Filter active jobs
        active_jobs = JobListing.objects.filter(status="ACTIVE")
        self.assertEqual(active_jobs.count(), 1)
        self.assertEqual(active_jobs.first(), active_job)
        
        # Filter closed jobs
        closed_jobs = JobListing.objects.filter(status="CLOSED")
        self.assertEqual(closed_jobs.count(), 1)
        self.assertEqual(closed_jobs.first(), closed_job)
    
    def test_job_listing_filtering_by_location(self):
        """Test filtering job listings by location"""
        # Create job listings with different locations
        warsaw_job = JobListing.objects.create(
            job_title="Warsaw Job",
            company_name="Company",
            about_company="About company",
            job_description="Job description",
            location=self.location
        )
        
        krakow_location = Location.objects.create(country="Poland", city="Krakow")
        krakow_job = JobListing.objects.create(
            job_title="Krakow Job",
            company_name="Company",
            about_company="About company",
            job_description="Job description",
            location=krakow_location
        )
        
        # Filter by Warsaw location
        warsaw_jobs = JobListing.objects.filter(location=self.location)
        self.assertEqual(warsaw_jobs.count(), 1)
        self.assertEqual(warsaw_jobs.first(), warsaw_job)
        
        # Filter by Krakow location
        krakow_jobs = JobListing.objects.filter(location=krakow_location)
        self.assertEqual(krakow_jobs.count(), 1)
        self.assertEqual(krakow_jobs.first(), krakow_job)


@pytest.mark.django_db
class TestJobModels:
    """Pytest-style tests for job models"""
    
    def test_job_listing_creation_with_factory(self, job_listing_factory):
        """Test creating job listing with factory"""
        job_listing = job_listing_factory()
        assert job_listing.job_title is not None
        assert job_listing.company_name is not None
        assert job_listing.job_description is not None
        assert job_listing.salary_currency in ['PLN', 'EUR', 'USD']
        assert job_listing.job_model in ['STATIONARY', 'HYBRID', 'REMOTE']
        assert job_listing.status in ['ACTIVE', 'CLOSED', 'ARCHIVED']
    
    def test_job_listing_skill_relationship(self, job_listing_factory, skill_factory):
        """Test job listing-skill relationship"""
        job_listing = job_listing_factory()
        skill = skill_factory()
        
        job_listing_skill = JobListingSkill.objects.create(
            job_listing=job_listing,
            skill=skill,
            level=5
        )
        
        assert job_listing_skill.job_listing == job_listing
        assert job_listing_skill.skill == skill
        assert job_listing_skill.level == 5


@pytest.mark.django_db
class TestJobViews:
    """Pytest-style tests for job views"""
    
    def test_job_listings_view(self, client):
        """Test job listings view"""
        response = client.get(reverse('job_listings'))
        assert response.status_code == 200
        assert 'jobs/listings.html' in [t.name for t in response.templates]
    
    def test_job_listing_details_view(self, client, job_listing_factory):
        """Test job listing details view"""
        job_listing = job_listing_factory()
        response = client.get(
            reverse('listing_details', kwargs={'listing_id': job_listing.id})
        )
        assert response.status_code == 200
        assert 'jobs/listing_details.html' in [t.name for t in response.templates]
    
    def test_add_listing_view_authenticated(self, authenticated_client):
        """Test add listing view for authenticated user"""
        response = authenticated_client.get(reverse('add_listing'))
        assert response.status_code == 200
        assert 'jobs/add_listing.html' in [t.name for t in response.templates]
    
    def test_add_listing_view_unauthenticated(self, client):
        """Test add listing view for unauthenticated user"""
        response = client.get(reverse('add_listing'))
        assert response.status_code == 302  # Redirect to login


@pytest.mark.django_db
class TestJobForms:
    """Pytest-style tests for job forms"""
    
    def test_job_listing_form_valid(self):
        """Test valid job listing form"""
        form_data = {
            'job_title': 'Software Engineer',
            'company_name': 'Tech Corp',
            'about_company': 'About company',
            'job_description': 'Job description',
            'salary_min': 5000,
            'salary_max': 8000,
            'salary_currency': 'PLN',
            'job_model': 'REMOTE',
            'status': 'ACTIVE'
        }
        
        form = JobListingForm(data=form_data)
        assert form.is_valid()
    
    def test_job_listing_form_missing_required_fields(self):
        """Test job listing form with missing required fields"""
        form_data = {
            'company_name': 'Tech Corp',
            'about_company': 'About company'
            # Missing job_title and job_description
        }
        
        form = JobListingForm(data=form_data)
        assert not form.is_valid()
        assert 'job_title' in form.errors
        assert 'job_description' in form.errors
