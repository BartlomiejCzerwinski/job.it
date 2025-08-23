import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from unittest.mock import patch, MagicMock

from applications.models import Application
from users.models import AppUser, Location
from jobs.models import JobListing


class ApplicationModelTest(TestCase):
    """Test Application model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
        
        self.recruiter_user = User.objects.create_user(
            username="recruiter",
            email="recruiter@example.com",
            password="recruiterpass123"
        )
        self.recruiter_app_user = AppUser.objects.create(
            user=self.recruiter_user,
            role="recruiter"
        )
        
        self.location = Location.objects.create(
            country="Poland",
            city=f"Warsaw-{self.__class__.__name__}"
        )
        
        self.job_listing = JobListing.objects.create(
            job_title="Software Engineer",
            company_name="Tech Corp",
            about_company="About company",
            job_description="Job description",
            owner=self.recruiter_app_user
        )
    
    def test_application_creation(self):
        """Test creating an application"""
        application = Application.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user,
            status="PENDING"
        )
        
        self.assertEqual(application.job_listing, self.job_listing)
        self.assertEqual(application.candidate, self.app_user)
        self.assertEqual(application.status, "PENDING")
    
    def test_application_default_status(self):
        """Test application default status"""
        application = Application.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user
        )
        
        self.assertEqual(application.status, "PENDING")
    
    def test_application_status_choices(self):
        """Test application status choices"""
        valid_statuses = ["PENDING", "ACCEPTED", "REJECTED"]
        
        # Create different job listings for each status to avoid unique constraint violation
        for i, status in enumerate(valid_statuses):
            job_listing = JobListing.objects.create(
                job_title=f"Software Engineer {i}",
                company_name=f"Tech Corp {i}",
                about_company="About company",
                job_description="Job description",
                owner=self.recruiter_app_user
            )
            
            application = Application.objects.create(
                job_listing=job_listing,
                candidate=self.app_user,
                status=status
            )
            self.assertEqual(application.status, status)
    
    def test_application_str_representation(self):
        """Test string representation of application"""
        application = Application.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user
        )
        
        expected_str = f"Application for {self.job_listing.job_title} by {self.app_user}"
        self.assertEqual(str(application), expected_str)
    
    def test_application_unique_constraint(self):
        """Test that user can only apply once to the same job"""
        Application.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user,

        )
        
        # Should not be able to apply again to the same job
        with self.assertRaises(IntegrityError):
            Application.objects.create(
                job_listing=self.job_listing,
                candidate=self.app_user,
    
            )
    
    def test_application_applied_at_auto_set(self):
        """Test that applied_at is automatically set"""
        application = Application.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user
        )
        
        # applied_at should be set automatically
        self.assertIsNotNone(application.applied_at)



class ApplicationUtilsTest(TestCase):
    """Test application utility functions"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
        
        self.recruiter_user = User.objects.create_user(
            username="recruiter",
            email="recruiter@example.com",
            password="recruiterpass123"
        )
        self.recruiter_app_user = AppUser.objects.create(
            user=self.recruiter_user,
            role="recruiter"
        )
        
        self.location = Location.objects.create(
            country="Poland",
            city=f"Warsaw-{self.__class__.__name__}"
        )
        
        self.job_listing = JobListing.objects.create(
            job_title="Software Engineer",
            company_name="Tech Corp",
            about_company="About company",
            job_description="Job description",
            owner=self.recruiter_app_user
        )
    
    def test_application_status_transitions(self):
        """Test application status transitions"""
        application = Application.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user
        )
        
        # Initial status should be PENDING
        self.assertEqual(application.status, "PENDING")
        
        # Can change to ACCEPTED
        application.status = "ACCEPTED"
        application.save()
        self.assertEqual(application.status, "ACCEPTED")
        
        # Can change to REJECTED
        application.status = "REJECTED"
        application.save()
        self.assertEqual(application.status, "REJECTED")
    
    def test_application_filtering_by_status(self):
        """Test filtering applications by status"""
        # Create applications with different statuses
        pending_app = Application.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user,

        )
        
        accepted_app = Application.objects.create(
            job_listing=self.job_listing,
            candidate=AppUser.objects.create(
                user=User.objects.create_user(
                    username="user2",
                    email="user2@example.com",
                    password="pass123"
                )
            ),

            status="ACCEPTED"
        )
        
        # Filter pending applications
        pending_apps = Application.objects.filter(status="PENDING")
        self.assertEqual(pending_apps.count(), 1)
        self.assertEqual(pending_apps.first(), pending_app)
        
        # Filter accepted applications
        accepted_apps = Application.objects.filter(status="ACCEPTED")
        self.assertEqual(accepted_apps.count(), 1)
        self.assertEqual(accepted_apps.first(), accepted_app)
    
    def test_application_filtering_by_candidate(self):
        """Test filtering applications by candidate"""
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123"
        )
        other_app_user = AppUser.objects.create(user=other_user)
        
        # Create applications for different users
        my_app = Application.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user,

        )
        
        other_app = Application.objects.create(
            job_listing=self.job_listing,
            candidate=other_app_user,

        )
        
        # Filter by current user
        my_apps = Application.objects.filter(candidate=self.app_user)
        self.assertEqual(my_apps.count(), 1)
        self.assertEqual(my_apps.first(), my_app)
        
        # Filter by other user
        other_apps = Application.objects.filter(candidate=other_app_user)
        self.assertEqual(other_apps.count(), 1)
        self.assertEqual(other_apps.first(), other_app)
    
    def test_application_filtering_by_job_listing(self):
        """Test filtering applications by job listing"""
        other_job = JobListing.objects.create(
            job_title="Other Job",
            company_name="Other Company",
            about_company="About other company",
            job_description="Other job description",
            owner=self.recruiter_app_user
        )
        
        # Create applications for different jobs
        job1_app = Application.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user,

        )
        
        job2_app = Application.objects.create(
            job_listing=other_job,
            candidate=self.app_user,

        )
        
        # Filter by first job
        job1_apps = Application.objects.filter(job_listing=self.job_listing)
        self.assertEqual(job1_apps.count(), 1)
        self.assertEqual(job1_apps.first(), job1_app)
        
        # Filter by second job
        job2_apps = Application.objects.filter(job_listing=other_job)
        self.assertEqual(job2_apps.count(), 1)
        self.assertEqual(job2_apps.first(), job2_app)



@pytest.mark.django_db
class TestApplicationModels:
    """Pytest-style tests for application models"""
    
    def test_application_creation_with_factory(self, application_factory):
        """Test creating application with factory"""
        application = application_factory()
        assert application.job_listing is not None
        assert application.candidate is not None
        assert application.status in ['PENDING', 'ACCEPTED', 'REJECTED']
    
    def test_application_unique_constraint(self, application_factory, job_listing_factory, app_user_factory):
        """Test application unique constraint"""
        job_listing = job_listing_factory()
        candidate = app_user_factory()
        
        # Create first application
        application1 = application_factory(
            job_listing=job_listing,
            candidate=candidate
        )
        
        # Should not be able to create duplicate
        with pytest.raises(IntegrityError):
            application_factory(
                job_listing=job_listing,
                candidate=candidate
            )



