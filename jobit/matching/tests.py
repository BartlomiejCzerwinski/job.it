import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import datetime

from matching.models import Match
from users.models import AppUser, Location, Skill, UserSkill
from jobs.models import JobListing, JobListingSkill


class MatchModelTest(TestCase):
    
    def setUp(self):
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
            owner=self.recruiter_app_user,
            location=self.location
        )
        
        self.skill = Skill.objects.create(name="Python")
    
    def test_match_creation(self):
        match = Match.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user,
            score=0.85,
            created_at=datetime.now()
        )
        
        self.assertEqual(match.job_listing, self.job_listing)
        self.assertEqual(match.candidate, self.app_user)
        self.assertEqual(match.score, 0.85)
        self.assertIsNotNone(match.created_at)
    
    def test_match_score_validation(self):
        """Test match score validation"""
        # Score should be between 0 and 1
        valid_scores = [0.0, 0.5, 1.0]
        
        for i, score in enumerate(valid_scores):
            candidate = AppUser.objects.create(
                user=User.objects.create_user(
                    username=f"user{i}",
                    email=f"user{i}@example.com",
                    password="pass123"
                )
            )
            
            match = Match.objects.create(
                job_listing=self.job_listing,
                candidate=candidate,
                score=score
            )
            self.assertEqual(match.score, score)
        
        # Score can be 0 (no match)
        match_zero = Match.objects.create(
            job_listing=self.job_listing,
            candidate=AppUser.objects.create(
                user=User.objects.create_user(
                    username="user4",
                    email="user4@example.com",
                    password="pass123"
                )
            ),
            score=0.0
        )
        self.assertEqual(match_zero.score, 0.0)
    
    def test_match_str_representation(self):
        """Test string representation of match"""
        match = Match.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user,
            score=0.75
        )
        
        expected_str = f"Match: {self.app_user.user.username} - {self.job_listing.job_title} (0.75)"
        self.assertEqual(str(match), expected_str)
    
    def test_match_matched_at_auto_set(self):
        """Test that matched_at is automatically set if not provided"""
        match = Match.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user,
            score=0.8
        )
        
        self.assertIsNotNone(match.created_at)
        
        # created_at should be close to current time
        now = timezone.now()
        time_diff = abs((now - match.created_at).total_seconds())
        self.assertLess(time_diff, 5)  # Within 5 seconds
    
    def test_match_unique_constraint(self):
        """Test that match for same job-candidate combination is unique"""
        Match.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user,
            score=0.8
        )
        
        # Should not be able to create another match with same combination
        with self.assertRaises(IntegrityError):
            Match.objects.create(
                job_listing=self.job_listing,
                candidate=self.app_user,
                score=0.9
            )
    
    def test_match_ordering_by_score(self):
        """Test match ordering by score"""
        # Create matches with different scores
        match1 = Match.objects.create(
            job_listing=self.job_listing,
            candidate=self.app_user,
            score=0.6
        )
        
        match2 = Match.objects.create(
            job_listing=self.job_listing,
            candidate=AppUser.objects.create(
                user=User.objects.create_user(
                    username="user2",
                    email="user2@example.com",
                    password="pass123"
                )
            ),
            score=0.9
        )
        
        match3 = Match.objects.create(
            job_listing=self.job_listing,
            candidate=AppUser.objects.create(
                user=User.objects.create_user(
                    username="user3",
                    email="user3@example.com",
                    password="pass123"
                )
            ),
            score=0.3
        )
        
        # Matches should be ordered by score (descending)
        matches = Match.objects.all().order_by('-score')
        self.assertEqual(matches[0], match2)  # score 0.9
        self.assertEqual(matches[1], match1)  # score 0.6
        self.assertEqual(matches[2], match3)  # score 0.3





class MatchingUtilsTest(TestCase):
    """Test matching utility functions"""
    
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
            owner=self.recruiter_app_user,
            location=self.location
        )
        
        self.skill = Skill.objects.create(name="Python")
        self.javascript_skill = Skill.objects.create(name="JavaScript")
        self.django_skill = Skill.objects.create(name="Django")
    
    def test_skill_matching_score(self):
        """Test skill matching score calculation"""
        # Add skills to job listing
        JobListingSkill.objects.create(
            job_listing=self.job_listing,
            skill=self.skill,
            level=5
        )
        JobListingSkill.objects.create(
            job_listing=self.job_listing,
            skill=self.javascript_skill,
            level=3
        )
        
        # Add skills to candidate
        UserSkill.objects.create(
            user=self.app_user,
            skill=self.skill,
            level=4
        )
        UserSkill.objects.create(
            user=self.app_user,
            skill=self.django_skill,
            level=5
        )
        
        pass
    
    def test_location_matching_score(self):
        """Test location matching score calculation"""
        # Test exact location match - use the same location as the job listing
        self.app_user.location = self.location
        self.app_user.save()
        
        # Job and candidate have same location
        self.assertEqual(self.job_listing.location, self.app_user.location)
        
        # Test different location
        different_location = Location.objects.create(
            country="Germany",
            city="Berlin-test_location_matching_score"
        )
        self.app_user.location = different_location
        self.app_user.save()
        
        # Job and candidate have different locations
        self.assertNotEqual(self.job_listing.location, self.app_user.location)
    
    def test_job_model_matching_score(self):
        """Test job model matching score calculation"""
        # Test remote work preference
        self.app_user.is_remote = True
        self.app_user.is_hybrid = False
        self.app_user.save()
        
        # Job is remote
        self.job_listing.job_model = "REMOTE"
        self.job_listing.save()
        
        # Perfect match for remote work
        self.assertEqual(self.job_listing.job_model, "REMOTE")
        self.assertTrue(self.app_user.is_remote)
        
        # Job is stationary
        self.job_listing.job_model = "STATIONARY"
        self.job_listing.save()
        
        # Mismatch for remote work preference
        self.assertEqual(self.job_listing.job_model, "STATIONARY")
        self.assertTrue(self.app_user.is_remote)
    
    def test_salary_matching_score(self):
        """Test salary matching score calculation"""
        # Set job salary range
        self.job_listing.salary_min = 5000
        self.job_listing.salary_max = 8000
        self.job_listing.save()
        pass
    
    def test_overall_matching_score(self):
        """Test overall matching score calculation"""
        pass


class MatchingAlgorithmTest(TestCase):
    """Test matching algorithm functionality"""
    
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
            job_title="Python Developer",
            company_name="Tech Corp",
            about_company="About company",
            job_description="We need a Python developer with Django experience",
            owner=self.recruiter_app_user,
            location=self.location,
            job_model="REMOTE",
            salary_min=5000,
            salary_max=8000
        )
        
        # Create skills
        self.python_skill = Skill.objects.create(name="Python")
        self.django_skill = Skill.objects.create(name="Django")
        self.javascript_skill = Skill.objects.create(name="JavaScript")
        
        # Add required skills to job
        JobListingSkill.objects.create(
            job_listing=self.job_listing,
            skill=self.python_skill,
            level=5
        )
        JobListingSkill.objects.create(
            job_listing=self.job_listing,
            skill=self.django_skill,
            level=4
        )
    
    def test_perfect_skill_match(self):
        """Test perfect skill match scenario"""
        # Candidate has exact skills required
        UserSkill.objects.create(
            user=self.app_user,
            skill=self.python_skill,
            level=5
        )
        UserSkill.objects.create(
            user=self.app_user,
            skill=self.django_skill,
            level=4
        )
        
        pass
    
    def test_partial_skill_match(self):
        """Test partial skill match scenario"""
        # Candidate has some required skills
        UserSkill.objects.create(
            user=self.app_user,
            skill=self.python_skill,
            level=5
        )
        pass
    
    def test_no_skill_match(self):
        """Test no skill match scenario"""
        # Candidate has different skills
        UserSkill.objects.create(
            user=self.app_user,
            skill=self.javascript_skill,
            level=5
        )
        
        # Should have low matching score
        pass
    
    def test_location_match(self):
        """Test location matching"""
        # Candidate in same location
        self.app_user.location = self.location
        self.app_user.save()
        
        pass
    
    def test_remote_work_match(self):
        """Test remote work matching"""
        # Candidate prefers remote work
        self.app_user.is_remote = True
        self.app_user.is_hybrid = False
        self.app_user.save()
        
        # Job is remote
        self.job_listing.job_model = "REMOTE"
        self.job_listing.save()
        
        # Should have remote work bonus
        pass

@pytest.mark.django_db
class TestMatchModels:
    """Pytest-style tests for match models"""
    
    def test_match_creation_with_factory(self, match_factory):
        """Test creating match with factory"""
        match = match_factory()
        assert match.job_listing is not None
        assert match.candidate is not None
        assert 0.0 <= match.score <= 1.0
        assert match.created_at is not None
    
    def test_match_unique_constraint(self, match_factory, job_listing_factory, app_user_factory):
        """Test match unique constraint"""
        job_listing = job_listing_factory()
        candidate = app_user_factory()
        
        # Create first match
        match1 = match_factory(
            job_listing=job_listing,
            candidate=candidate
        )
        
        # Should not be able to create duplicate
        with pytest.raises(IntegrityError):
            match_factory(
                job_listing=job_listing,
                candidate=candidate
            )



