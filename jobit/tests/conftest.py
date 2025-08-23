import pytest
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, Sequence

# =============================================================================
# FACTORY FUNCTIONS FOR CREATING TEST DATA
# =============================================================================

def get_location_factory():
    """Get LocationFactory with proper Django model reference"""
    from users.models import Location
    
    class LocationFactory(DjangoModelFactory):
        class Meta:
            model = Location
        
        country = Faker('country')
        city = Sequence(lambda n: f"TestCity{n}")
    
    return LocationFactory


def get_skill_factory():
    """Get SkillFactory with proper Django model reference"""
    from users.models import Skill
    
    class SkillFactory(DjangoModelFactory):
        class Meta:
            model = Skill
        
        name = Faker('word')
    
    return SkillFactory


def get_user_factory():
    """Get UserFactory with proper Django model reference"""
    from django.contrib.auth.models import User
    
    class UserFactory(DjangoModelFactory):
        class Meta:
            model = User
        
        username = Sequence(lambda n: f'user{n}')
        email = Faker('email')
        first_name = Faker('first_name')
        last_name = Faker('last_name')
        password = Faker('password', length=12)
    
    return UserFactory


def get_app_user_factory():
    """Get AppUserFactory with proper Django model reference"""
    from users.models import AppUser
    
    class AppUserFactory(DjangoModelFactory):
        class Meta:
            model = AppUser
        
        user = SubFactory(get_user_factory())
        about_me = Faker('text', max_nb_chars=200)
        full_name = Faker('name')
        mobile = Faker('phone_number')
        position = Faker('job')
        location = SubFactory(get_location_factory())
        is_remote = Faker('boolean')
        is_hybrid = Faker('boolean')
        starts_in = Faker('random_element', elements=['ASAP', '2 weeks', '1 month', '3 months'])
        role = Faker('random_element', elements=['recruiter', 'worker'])
    
    return AppUserFactory


def get_job_listing_factory():
    """Get JobListingFactory with proper Django model reference"""
    from jobs.models import JobListing
    
    class JobListingFactory(DjangoModelFactory):
        class Meta:
            model = JobListing
        
        job_title = Faker('job')
        company_name = Faker('company')
        about_company = Faker('text', max_nb_chars=300)
        job_description = Faker('text', max_nb_chars=500)
        salary_min = Faker('random_int', min=3000, max=15000)
        salary_max = Faker('random_int', min=15000, max=30000)
        salary_currency = Faker('random_element', elements=['PLN', 'EUR', 'USD'])
        location = SubFactory(get_location_factory())
        job_model = Faker('random_element', elements=['STATIONARY', 'HYBRID', 'REMOTE'])
        owner = SubFactory(get_app_user_factory())
        status = Faker('random_element', elements=['ACTIVE', 'CLOSED', 'ARCHIVED'])
    
    return JobListingFactory


def get_application_factory():
    """Get ApplicationFactory with proper Django model reference"""
    from applications.models import Application
    
    class ApplicationFactory(DjangoModelFactory):
        class Meta:
            model = Application
        
        job_listing = SubFactory(get_job_listing_factory())
        candidate = SubFactory(get_app_user_factory())
        status = Faker('random_element', elements=['PENDING', 'ACCEPTED', 'REJECTED'])
    
    return ApplicationFactory


def get_conversation_factory():
    """Get ConversationFactory with proper Django model reference"""
    from chat.models import Conversation
    
    class ConversationFactory(DjangoModelFactory):
        class Meta:
            model = Conversation
        
        job_listing = SubFactory(get_job_listing_factory())
        candidate = SubFactory(get_user_factory())
        recruiter = SubFactory(get_user_factory())
    
    return ConversationFactory


def get_message_factory():
    """Get MessageFactory with proper Django model reference"""
    from chat.models import Message
    
    class MessageFactory(DjangoModelFactory):
        class Meta:
            model = Message
        
        conversation = SubFactory(get_conversation_factory())
        sender = SubFactory(get_user_factory())
        content = Faker('text', max_nb_chars=200)
    
    return MessageFactory


def get_match_factory():
    """Get MatchFactory with proper Django model reference"""
    from matching.models import Match
    
    class MatchFactory(DjangoModelFactory):
        class Meta:
            model = Match
        
        job_listing = SubFactory(get_job_listing_factory())
        candidate = SubFactory(get_app_user_factory())
        score = Faker('random_float', min=0.0, max=1.0)
    
    return MatchFactory


@pytest.fixture
def client():
    """Django test client"""
    from django.test import Client
    return Client()


@pytest.fixture
def user_factory():
    """Factory for creating User instances"""
    return get_user_factory()


@pytest.fixture
def app_user_factory():
    """Factory for creating AppUser instances"""
    return get_app_user_factory()


@pytest.fixture
def location_factory():
    """Factory for creating Location instances"""
    return get_location_factory()


@pytest.fixture
def skill_factory():
    """Factory for creating Skill instances"""
    return get_skill_factory()


@pytest.fixture
def job_listing_factory():
    """Factory for creating JobListing instances"""
    return get_job_listing_factory()


@pytest.fixture
def application_factory():
    """Factory for creating Application instances"""
    return get_application_factory()


@pytest.fixture
def conversation_factory():
    """Factory for creating Conversation instances"""
    return get_conversation_factory()


@pytest.fixture
def message_factory():
    """Factory for creating Message instances"""
    return get_message_factory()


@pytest.fixture
def match_factory():
    """Factory for creating Match instances"""
    return get_match_factory()


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return get_user_factory()()


@pytest.fixture
def sample_app_user():
    """Create a sample app user for testing"""
    return get_app_user_factory()()


@pytest.fixture
def sample_location():
    """Create a sample location for testing"""
    return get_location_factory()()


@pytest.fixture
def sample_skill():
    """Create a sample skill for testing"""
    return get_skill_factory()()


@pytest.fixture
def sample_job_listing():
    """Create a sample job listing for testing"""
    return get_job_listing_factory()()


@pytest.fixture
def sample_application():
    """Create a sample application for testing"""
    return get_application_factory()()


@pytest.fixture
def authenticated_client(client, sample_user):
    """Client authenticated with a sample user"""
    client.force_login(sample_user)
    return client


@pytest.fixture
def recruiter_user():
    """Create a user with recruiter role"""
    user = get_user_factory()()
    app_user = get_app_user_factory()(user=user, role='recruiter')
    return user


@pytest.fixture
def worker_user():
    """Create a user with worker role"""
    user = get_user_factory()()
    app_user = get_app_user_factory()(user=user, role='worker')
    return user


@pytest.fixture
def sample_recruiter():
    """Create a sample recruiter for testing"""
    return get_app_user_factory()(role='recruiter')


@pytest.fixture
def sample_worker():
    """Create a sample worker for testing"""
    return get_app_user_factory()(role='worker')
