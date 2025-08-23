import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from unittest.mock import patch, MagicMock
import base64
import io

from users.models import AppUser, Location, Skill, UserSkill, SocialLink, Project
from users.views import register, add_profile_photo, get_profile_photo
from users.forms import RegisterForm


class LocationModelTest(TestCase):
    """Test Location model functionality"""
    
    def test_location_creation(self):
        """Test creating a location"""
        location = Location.objects.create(
            country="Poland",
            city="Warsaw-basic"
        )
        self.assertEqual(location.country, "Poland")
        self.assertEqual(location.city, "Warsaw-basic")
        self.assertEqual(str(location), "Warsaw-basic, Poland")
    
    def test_location_unique_constraint(self):
        """Test that country-city combination must be unique"""
        Location.objects.create(country="Poland", city="Warsaw-unique1")
        
        with self.assertRaises(IntegrityError):
            Location.objects.create(country="Poland", city="Warsaw-unique1")
    
    def test_location_str_representation(self):
        """Test string representation of location"""
        location = Location.objects.create(country="Germany", city="Berlin-test")
        self.assertEqual(str(location), "Berlin-test, Germany")


class SkillModelTest(TestCase):
    """Test Skill model functionality"""
    
    def test_skill_creation(self):
        """Test creating a skill"""
        skill = Skill.objects.create(name="Python")
        self.assertEqual(skill.name, "Python")
        self.assertEqual(skill.id, 1)
    
    def test_skill_str_representation(self):
        """Test string representation of skill"""
        skill = Skill.objects.create(name="JavaScript")
        self.assertEqual(str(skill), "JavaScript")


class AppUserModelTest(TestCase):
    """Test AppUser model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.location = Location.objects.create(
            country="Poland",
            city=f"Krakow-{self.__class__.__name__}"
        )
    
    def test_app_user_creation(self):
        """Test creating an app user"""
        app_user = AppUser.objects.create(
            user=self.user,
            about_me="I am a developer",
            full_name="John Doe",
            mobile="+48123456789",
            position="Software Engineer",
            location=self.location,
            is_remote=True,
            is_hybrid=False,
            starts_in="ASAP",
            role="worker"
        )
        
        self.assertEqual(app_user.user, self.user)
        self.assertEqual(app_user.about_me, "I am a developer")
        self.assertEqual(app_user.full_name, "John Doe")
        self.assertEqual(app_user.mobile, "+48123456789")
        self.assertEqual(app_user.position, "Software Engineer")
        self.assertEqual(app_user.location, self.location)
        self.assertTrue(app_user.is_remote)
        self.assertFalse(app_user.is_hybrid)
        self.assertEqual(app_user.starts_in, "ASAP")
        self.assertEqual(app_user.role, "worker")
    
    def test_app_user_default_values(self):
        """Test app user default values"""
        app_user = AppUser.objects.create(user=self.user)
        
        self.assertEqual(app_user.role, "worker")
        self.assertEqual(app_user.starts_in, "ASAP")
        self.assertFalse(app_user.is_remote)
        self.assertFalse(app_user.is_hybrid)
        self.assertIsNone(app_user.about_me)
        self.assertIsNone(app_user.full_name)
        self.assertIsNone(app_user.mobile)
        self.assertIsNone(app_user.position)
        self.assertIsNone(app_user.location)
    
    def test_app_user_role_choices(self):
        """Test app user role choices"""
        app_user = AppUser.objects.create(user=self.user, role="recruiter")
        self.assertEqual(app_user.role, "recruiter")
        
        # Test invalid role
        with self.assertRaises(ValidationError):
            app_user.role = "invalid_role"
            app_user.full_clean()
    
    def test_app_user_starts_in_choices(self):
        """Test app user starts_in choices"""
        valid_choices = ['ASAP', '2 weeks', '1 month', '3 months']
        
        for choice in valid_choices:
            app_user = AppUser.objects.create(user=self.user, starts_in=choice)
            self.assertEqual(app_user.starts_in, choice)


class UserSkillModelTest(TestCase):
    """Test UserSkill model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
        self.skill = Skill.objects.create(name="Python")
    
    def test_user_skill_creation(self):
        """Test creating a user skill"""
        user_skill = UserSkill.objects.create(
            user=self.app_user,
            skill=self.skill,
            level=5
        )
        
        self.assertEqual(user_skill.user, self.app_user)
        self.assertEqual(user_skill.skill, self.skill)
        self.assertEqual(user_skill.level, 5)
    
    def test_user_skill_level_validation(self):
        """Test user skill level validation"""
        # Level should be positive
        user_skill = UserSkill.objects.create(
            user=self.app_user,
            skill=self.skill,
            level=1
        )
        self.assertEqual(user_skill.level, 1)
        
        # Level can be 0 (beginner)
        user_skill.level = 0
        user_skill.save()
        self.assertEqual(user_skill.level, 0)


class SocialLinkModelTest(TestCase):
    """Test SocialLink model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
    
    def test_social_link_creation(self):
        """Test creating a social link"""
        social_link = SocialLink.objects.create(
            user=self.app_user,
            platform="github",
            url="https://github.com/testuser",
            display_name="My GitHub"
        )
        
        self.assertEqual(social_link.user, self.app_user)
        self.assertEqual(social_link.platform, "github")
        self.assertEqual(social_link.url, "https://github.com/testuser")
        self.assertEqual(social_link.display_name, "My GitHub")
    
    def test_social_link_platform_choices(self):
        """Test social link platform choices"""
        valid_platforms = [
            'website', 'github', 'linkedin', 'gitlab', 'stackoverflow',
            'medium', 'devto', 'portfolio', 'other'
        ]
        
        for platform in valid_platforms:
            social_link = SocialLink.objects.create(
                user=self.app_user,
                platform=platform,
                url=f"https://{platform}.com/testuser"
            )
            self.assertEqual(social_link.platform, platform)
    
    def test_social_link_str_representation(self):
        """Test string representation of social link"""
        social_link = SocialLink.objects.create(
            user=self.app_user,
            platform="linkedin",
            url="https://linkedin.com/in/testuser"
        )
        expected_str = f"{self.app_user.user.email}'s linkedin link"
        self.assertEqual(str(social_link), expected_str)


class ProjectModelTest(TestCase):
    """Test Project model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
    
    def test_project_creation(self):
        """Test creating a project"""
        project = Project.objects.create(
            user=self.app_user,
            title="My Project",
            description="A test project",
            technologies="Python, Django, JavaScript",
            github_link="https://github.com/testuser/project",
            demo_link="https://demo.example.com",
            order=1
        )
        
        self.assertEqual(project.user, self.app_user)
        self.assertEqual(project.title, "My Project")
        self.assertEqual(project.description, "A test project")
        self.assertEqual(project.technologies, "Python, Django, JavaScript")
        self.assertEqual(project.github_link, "https://github.com/testuser/project")
        self.assertEqual(project.demo_link, "https://demo.example.com")
        self.assertEqual(project.order, 1)
    
    def test_project_default_order(self):
        """Test project default order"""
        project = Project.objects.create(
            user=self.app_user,
            title="My Project",
            description="A test project"
        )
        self.assertEqual(project.order, 0)
    
    def test_project_ordering(self):
        """Test project ordering by order field"""
        project1 = Project.objects.create(
            user=self.app_user,
            title="Project 1",
            description="First project",
            order=2
        )
        project2 = Project.objects.create(
            user=self.app_user,
            title="Project 2",
            description="Second project",
            order=1
        )
        
        projects = Project.objects.all()
        self.assertEqual(projects[0], project2)  # order=1 comes first
        self.assertEqual(projects[1], project1)  # order=2 comes second


class UserViewsTest(TestCase):
    """Test user views functionality"""
    
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
            city="Warsaw"
        )
    
    def test_register_view_get(self):
        """Test register view GET request"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
    
    def test_register_view_post_success(self):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'role': 'worker'
        }
        
        response = self.client.post(reverse('register'), data)
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        
        # Check if user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(AppUser.objects.filter(user__username='newuser').exists())
    
    def test_register_view_post_invalid_data(self):
        """Test user registration with invalid data"""
        data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'invalid-email',
            'password': 'newpass123',
            'repeated_password': 'differentpass',
            'role': 'worker'
        }
        
        response = self.client.post(reverse('register'), data)
        
        # Should return to form with errors
        self.assertEqual(response.status_code, 200)
        # Should have form errors for invalid data
    
    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
    
    def test_login_view_post_success(self):
        """Test successful login"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(reverse('login'), data)
        
        # Should redirect to home page
        self.assertEqual(response.status_code, 302)
        
        # Check if user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_view_post_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(reverse('login'), data)
        
        # Should return to form with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')


class UserFormsTest(TestCase):
    """Test user forms functionality"""
    
    def test_user_registration_form_valid(self):
        """Test valid user registration form"""
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'repeated_password': 'newpass123',
            'role': 'worker',
            'position': 'Developer',
            'country': 'Poland',
            'city': 'Warsaw',
            'starts_in': 'ASAP'
        }
        
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_user_registration_form_password_mismatch(self):
        """Test user registration form with password mismatch"""
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'repeated_password': 'differentpass',
            'role': 'worker'
        }
        
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Should have form errors for password mismatch
    
    def test_user_registration_form_invalid_email(self):
        """Test user registration form with invalid email"""
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'invalid-email',
            'password': 'newpass123',
            'repeated_password': 'newpass123',
            'role': 'worker'
        }
        
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class UserUtilsTest(TestCase):
    """Test user utility functions"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
    
    @patch('users.views.settings.AZURE_STORAGE_CONNECTION_STRING', 'fake_connection_string')
    @patch('users.views.BlobServiceClient')
    def test_add_profile_photo_success(self, mock_blob_service):
        """Test successful profile photo upload"""
        # Mock Azure Blob Storage
        mock_blob_service.from_connection_string.return_value.get_container_client.return_value.get_blob_client.return_value.upload_blob.return_value = None
        
        # Create a fake image file
        fake_image = io.BytesIO(b'fake_image_data')
        fake_image.name = 'test.jpg'
        
        result = add_profile_photo(self.user.id, fake_image)
        self.assertTrue(result)
    
    @patch('users.views.settings.AZURE_STORAGE_CONNECTION_STRING', 'fake_connection_string')
    @patch('users.views.BlobServiceClient')
    def test_add_profile_photo_failure(self, mock_blob_service):
        """Test profile photo upload failure"""
        # Mock Azure Blob Storage to raise an exception
        mock_blob_service.from_connection_string.side_effect = Exception("Azure error")
        
        fake_image = io.BytesIO(b'fake_image_data')
        fake_image.name = 'test.jpg'
        
        result = add_profile_photo(self.user.id, fake_image)
        self.assertFalse(result)
    
    @patch('users.views.settings.AZURE_STORAGE_CONNECTION_STRING', 'fake_connection_string')
    @patch('users.views.BlobServiceClient')
    def test_get_profile_photo_success(self, mock_blob_service):
        """Test successful profile photo retrieval"""
        # Mock Azure Blob Storage
        mock_blob_client = MagicMock()
        mock_blob_client.exists.return_value = True
        mock_blob_client.download_blob.return_value.readall.return_value = b'fake_image_data'
        
        mock_blob_service.from_connection_string.return_value.get_container_client.return_value.get_blob_client.return_value = mock_blob_client
        
        result = get_profile_photo(self.user.id)
        self.assertIsNotNone(result)
        self.assertEqual(result, base64.b64encode(b'fake_image_data').decode('utf-8'))
    
    @patch('users.views.settings.AZURE_STORAGE_CONNECTION_STRING', 'fake_connection_string')
    @patch('users.views.BlobServiceClient')
    def test_get_profile_photo_not_found(self, mock_blob_service):
        """Test profile photo retrieval when photo doesn't exist"""
        # Mock Azure Blob Storage
        mock_blob_client = MagicMock()
        mock_blob_client.exists.return_value = False
        
        mock_blob_service.from_connection_string.return_value.get_container_client.return_value.get_blob_client.return_value = mock_blob_client
        
        result = get_profile_photo(self.user.id)
        self.assertIsNone(result)
    
    @patch('users.views.settings.AZURE_STORAGE_CONNECTION_STRING', 'fake_connection_string')
    @patch('users.views.BlobServiceClient')
    def test_get_profile_photo_failure(self, mock_blob_service):
        """Test profile photo retrieval failure"""
        # Mock Azure Blob Storage to raise an exception
        mock_blob_service.from_connection_string.side_effect = Exception("Azure error")
        
        result = get_profile_photo(self.user.id)
        self.assertIsNone(result)


@pytest.mark.django_db
class TestUserModels:
    """Pytest-style tests for user models"""
    
    def test_app_user_creation_with_factory(self, app_user_factory):
        """Test creating app user with factory"""
        app_user = app_user_factory()
        assert app_user.user is not None
        assert app_user.role in ['recruiter', 'worker']
        assert app_user.starts_in in ['ASAP', '2 weeks', '1 month', '3 months']
    
    def test_location_creation_with_factory(self, location_factory):
        """Test creating location with factory"""
        location = location_factory()
        assert location.country is not None
        assert location.city is not None
        assert str(location) == f"{location.city}, {location.country}"
    
    def test_skill_creation_with_factory(self, skill_factory):
        """Test creating skill with factory"""
        skill = skill_factory()
        assert skill.name is not None
        assert len(skill.name) > 0
    
    def test_user_skill_relationship(self, app_user_factory, skill_factory):
        """Test user-skill relationship"""
        app_user = app_user_factory()
        skill = skill_factory()
        
        user_skill = UserSkill.objects.create(
            user=app_user,
            skill=skill,
            level=5
        )
        
        assert user_skill.user == app_user
        assert user_skill.skill == skill
        assert user_skill.level == 5


@pytest.mark.django_db
class TestUserViews:
    """Pytest-style tests for user views"""
    
    def test_register_view_get(self, client):
        """Test register view GET request"""
        response = client.get(reverse('register'))
        assert response.status_code == 200
        assert 'users/register.html' in [t.name for t in response.templates]
    
    def test_register_view_post_success(self, client):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'role': 'worker'
        }
        
        response = client.post(reverse('register'), data)
        assert response.status_code == 302  # Redirect after success
        
        # Check if user was created
        assert User.objects.filter(username='newuser').exists()
        assert AppUser.objects.filter(user__username='newuser').exists()
    
    def test_login_view_authenticated_user(self, authenticated_client):
        """Test login view with authenticated user"""
        response = authenticated_client.get(reverse('login'))
        # Should redirect authenticated users
        assert response.status_code == 302


@pytest.mark.django_db
class TestUserForms:
    """Pytest-style tests for user forms"""
    
    def test_user_registration_form_valid(self):
        """Test valid user registration form"""
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'repeated_password': 'newpass123',
            'role': 'worker',
            'position': 'Developer',
            'country': 'Poland',
            'city': 'Warsaw',
            'starts_in': 'ASAP'
        }
        
        form = RegisterForm(data=form_data)
        assert form.is_valid()
    
    def test_user_registration_form_invalid_email(self):
        """Test user registration form with invalid email"""
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'role': 'worker'
        }
        
        form = RegisterForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors
