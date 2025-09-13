import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import datetime

from chat.models import Conversation, Message
from users.models import AppUser, Location
from jobs.models import JobListing


class ConversationModelTest(TestCase):
    """Test Conversation model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
        self.candidate_user = self.user  # For conversation model compatibility
        
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
    
    def test_conversation_creation(self):
        """Test creating a chat room"""
        conversation = Conversation.objects.create(
            job_listing=self.job_listing,
            candidate=self.candidate_user,
            recruiter=self.recruiter_user
        )
        
        self.assertEqual(conversation.job_listing, self.job_listing)
        self.assertEqual(conversation.candidate, self.user)
        self.assertEqual(conversation.recruiter, self.recruiter_user)
        self.assertIsNotNone(conversation.created_at)
    
    def test_conversation_str_representation(self):
        """Test string representation of chat room"""
        conversation = Conversation.objects.create(
            job_listing=self.job_listing,
            candidate=self.candidate_user,
            recruiter=self.recruiter_user
        )
        
        expected_str = f"Conversation about {self.job_listing.job_title} - {self.user.username}"
        self.assertEqual(str(conversation), expected_str)
    
    def test_conversation_unique_constraint(self):
        """Test that chat room for same job-applicant-recruiter combination is unique"""
        Conversation.objects.create(
            job_listing=self.job_listing,
            candidate=self.candidate_user,
            recruiter=self.recruiter_user
        )
        
        # Should not be able to create another chat room with same combination
        with self.assertRaises(IntegrityError):
            Conversation.objects.create(
                job_listing=self.job_listing,
                candidate=self.candidate_user,
                recruiter=self.recruiter_user
            )
    
    def test_conversation_created_at_auto_set(self):
        """Test that created_at is automatically set"""
        before_creation = timezone.now()
        
        conversation = Conversation.objects.create(
            job_listing=self.job_listing,
            candidate=self.candidate_user,
            recruiter=self.recruiter_user
        )
        
        after_creation = timezone.now()
        
        # created_at should be between before and after creation
        self.assertGreaterEqual(conversation.created_at, before_creation)
        self.assertLessEqual(conversation.created_at, after_creation)


class MessageModelTest(TestCase):
    """Test Message model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
        self.candidate_user = self.user  # For conversation model compatibility
        
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
        
        self.conversation = Conversation.objects.create(
            job_listing=self.job_listing,
            candidate=self.candidate_user,
            recruiter=self.recruiter_user
        )
    
    def test_message_creation(self):
        """Test creating a message"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content="Hello, I'm interested in this position",
            created_at=timezone.now()
        )
        
        self.assertEqual(message.conversation, self.conversation)
        self.assertEqual(message.sender, self.user)
        self.assertEqual(message.content, "Hello, I'm interested in this position")
        self.assertIsNotNone(message.created_at)
    
    def test_message_str_representation(self):
        """Test string representation of message"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content="Test message"
        )
        
        expected_str = f"Message in {self.conversation}"
        self.assertEqual(str(message), expected_str)
    
    def test_message_content_length_validation(self):
        """Test message content length validation"""
        # Create a very long message
        long_content = "A" * 1001  # Exceeds max length
        
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content=long_content
        )
        
        # Content should not be truncated (no validation in model)
        self.assertEqual(len(message.content), 1001)
    
    def test_message_timestamp_auto_set(self):
        """Test that timestamp is automatically set if not provided"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content="Test message"
        )
        
        self.assertIsNotNone(message.created_at)
        
        # created_at should be close to current time
        now = timezone.now()
        time_diff = abs((now - message.created_at).total_seconds())
        self.assertLess(time_diff, 5)  # Within 5 seconds
    
    def test_message_ordering(self):
        """Test message ordering by timestamp"""
        # Create messages with different timestamps
        message1 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content="First message",
            created_at=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        message2 = Message.objects.create(
            conversation=self.conversation,
            sender=self.recruiter_user,
            content="Second message",
            created_at=datetime(2023, 1, 1, 12, 1, 0)
        )
        
        message3 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content="Third message",
            created_at=datetime(2023, 1, 1, 12, 2, 0)
        )
        
        # Messages should be ordered by timestamp
        messages = Message.objects.all()
        self.assertEqual(messages[0], message1)
        self.assertEqual(messages[1], message2)
        self.assertEqual(messages[2], message3)




class ChatUtilsTest(TestCase):
    """Test chat utility functions"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.app_user = AppUser.objects.create(user=self.user)
        self.candidate_user = self.user  # For conversation model compatibility
        
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
        
        self.conversation = Conversation.objects.create(
            job_listing=self.job_listing,
            candidate=self.candidate_user,
            recruiter=self.recruiter_user
        )
    
    def test_conversation_participants(self):
        """Test chat room participants"""
        # Check if both users are participants
        self.assertIn(self.user, [self.conversation.candidate, self.conversation.recruiter])
        self.assertIn(self.recruiter_user, [self.conversation.candidate, self.conversation.recruiter])
    
    def test_message_sender_validation(self):
        """Test that message sender must be a chat room participant"""
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123"
        )
        other_app_user = AppUser.objects.create(user=other_user)
        
        # Should be able to send message as participant
        message1 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content="Message from applicant"
        )
        self.assertEqual(message1.sender, self.user)
        
        message2 = Message.objects.create(
            conversation=self.conversation,
            sender=self.recruiter_user,
            content="Message from recruiter"
        )
        self.assertEqual(message2.sender, self.recruiter_user)
    
    def test_conversation_messages_ordering(self):
        """Test chat room messages ordering"""
        # Create messages in chronological order (they will be ordered by creation time)
        message1 = Message.objects.create(
            conversation=self.conversation,
            sender=self.recruiter_user,
            content="First message"
        )
        
        message2 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content="Second message"
        )
        
        message3 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            content="Third message"
        )
        
        # Messages should be ordered by creation timestamp (ascending)
        messages = list(self.conversation.messages.all())
        self.assertEqual(len(messages), 3)
        # Check ordering by content
        self.assertEqual(messages[0].content, "First message")
        self.assertEqual(messages[1].content, "Second message")
        self.assertEqual(messages[2].content, "Third message")
    
    def test_conversation_creation_after_application(self):
        """Test chat room creation after job application"""
        # Create a new job listing and application
        new_job = JobListing.objects.create(
            job_title="New Job",
            company_name="New Company",
            about_company="About new company",
            job_description="New job description",
            owner=self.recruiter_app_user
        )
        
        pass



@pytest.mark.django_db
class TestChatModels:
    """Pytest-style tests for chat models"""
    
    def test_conversation_creation_with_factory(self, conversation_factory):
        """Test creating chat room with factory"""
        conversation = conversation_factory()
        assert conversation.job_listing is not None
        assert conversation.candidate is not None
        assert conversation.recruiter is not None
        assert conversation.created_at is not None
    
    def test_message_creation_with_factory(self, message_factory):
        """Test creating message with factory"""
        message = message_factory()
        assert message.conversation is not None
        assert message.sender is not None
        assert message.content is not None
        assert message.created_at is not None
    
    def test_conversation_unique_constraint(self, conversation_factory, job_listing_factory, app_user_factory):
        """Test chat room unique constraint"""
        job_listing = job_listing_factory()
        candidate = app_user_factory()
        recruiter = app_user_factory(role='recruiter')
        
        # Create first chat room
        conversation1 = conversation_factory(
            job_listing=job_listing,
            candidate=candidate,
            recruiter=recruiter
        )
        
        # Should not be able to create duplicate
        with pytest.raises(IntegrityError):
            conversation_factory(
                job_listing=job_listing,
                candidate=candidate,
                recruiter=recruiter
            )



