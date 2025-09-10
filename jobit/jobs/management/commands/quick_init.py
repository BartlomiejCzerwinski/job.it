from django.core.management.base import BaseCommand
from users.models import AppUser, Skill
from jobs.models import JobListing
from django.contrib.auth.models import User
import random


class Command(BaseCommand):
    help = 'Quick initialization with minimal sample data'

    def handle(self, *args, **options):
        try:
            # Check if we already have data
            candidates_count = AppUser.objects.filter(role='worker').count()
            jobs_count = JobListing.objects.count()
            
            if candidates_count > 0 and jobs_count > 0:
                self.stdout.write(self.style.SUCCESS('✅ Database already has sample data'))
                return
            
            # Create 3 quick candidates
            if candidates_count == 0:
                self.stdout.write('👥 Creating 3 quick candidates...')
                self.create_quick_candidates()
            
            # Create 3 quick jobs
            if jobs_count == 0:
                self.stdout.write('💼 Creating 3 quick job listings...')
                self.create_quick_jobs()
            
            self.stdout.write(self.style.SUCCESS('✅ Quick initialization complete!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during quick init: {str(e)}'))
    
    def create_quick_candidates(self):
        """Create 3 simple candidates quickly"""
        candidates_data = [
            {'name': 'John Smith', 'email': 'john.smith@example.com', 'position': 'Python Developer'},
            {'name': 'Jane Doe', 'email': 'jane.doe@example.com', 'position': 'React Developer'},
            {'name': 'Mike Johnson', 'email': 'mike.johnson@example.com', 'position': 'DevOps Engineer'}
        ]
        
        for data in candidates_data:
            try:
                # Create User
                user = User.objects.create_user(
                    username=data['email'],
                    email=data['email'],
                    password='password123',
                    first_name=data['name'].split()[0],
                    last_name=data['name'].split()[1]
                )
                
                # Create AppUser
                app_user = AppUser.objects.create(
                    user=user,
                    full_name=data['name'],
                    mobile=f"{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}",
                    position=data['position'],
                    role='worker',
                    about_me=f"I am a {data['position']} with experience in modern technologies."
                )
                
                # Add a few skills
                skills = Skill.objects.all()[:3]
                for skill in skills:
                    from users.models import UserSkill
                    UserSkill.objects.create(
                        user=app_user,
                        skill=skill,
                        level=random.randint(1, 3)
                    )
                
                self.stdout.write(f"✅ Created: {data['name']} - {data['position']}")
                
            except Exception as e:
                self.stdout.write(f"❌ Failed to create {data['name']}: {str(e)}")
    
    def create_quick_jobs(self):
        """Create 3 simple job listings quickly"""
        jobs_data = [
            {'title': 'Senior Python Developer', 'company': 'TechCorp', 'description': 'We need an experienced Python developer'},
            {'title': 'React Frontend Developer', 'company': 'WebSolutions', 'description': 'Looking for a skilled React developer'},
            {'title': 'DevOps Engineer', 'company': 'CloudTech', 'description': 'Join our DevOps team and help scale our infrastructure'}
        ]
        
        # Get or create a recruiter
        recruiter_email = 'recruiter@example.com'
        if not User.objects.filter(email=recruiter_email).exists():
            user = User.objects.create_user(
                username=recruiter_email,
                email=recruiter_email,
                password='password123',
                first_name='Recruiter',
                last_name='Smith'
            )
            app_user = AppUser.objects.create(
                user=user,
                full_name='Recruiter Smith',
                role='recruiter',
                position='HR Manager'
            )
        else:
            app_user = User.objects.get(email=recruiter_email).appuser
        
        for data in jobs_data:
            try:
                job = JobListing.objects.create(
                    job_title=data['title'],
                    company_name=data['company'],
                    about_company='A great company to work for',
                    job_description=data['description'],
                    salary_min=5000,
                    salary_max=10000,
                    salary_currency='PLN',
                    job_model='REMOTE',
                    owner=app_user,
                    status='ACTIVE'
                )
                
                # Add a few skills
                skills = Skill.objects.all()[:3]
                for skill in skills:
                    from jobs.models import JobListingSkill
                    JobListingSkill.objects.create(
                        job_listing=job,
                        skill=skill,
                        level=random.randint(1, 5)
                    )
                
                self.stdout.write(f"✅ Created: {data['title']} at {data['company']}")
                
            except Exception as e:
                self.stdout.write(f"❌ Failed to create {data['title']}: {str(e)}")
