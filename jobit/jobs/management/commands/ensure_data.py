from django.core.management.base import BaseCommand
from users.models import AppUser, Skill, Location, UserSkill
from jobs.models import JobListing, JobListingSkill
from django.contrib.auth.models import User
import random
import signal
import sys


class Command(BaseCommand):
    help = 'Ensure we have sufficient data for the app to work (10 candidates, 10 jobs)'

    def __init__(self):
        super().__init__()
        self.timeout_occurred = False

    def timeout_handler(self, signum, frame):
        self.timeout_occurred = True
        self.stdout.write(self.style.WARNING('⏰ Timeout reached, stopping data generation...'))
        sys.exit(0)

    def handle(self, *args, **options):
        # Set timeout to 3 minutes
        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(180)  # 3 minutes timeout
        
        try:
            # Check current data
            candidates_count = AppUser.objects.filter(role='worker').count()
            jobs_count = JobListing.objects.count()
            
            self.stdout.write(f'📊 Current data: {candidates_count} candidates, {jobs_count} jobs')
            
            # If we have sufficient data, we're good
            if candidates_count >= 10 and jobs_count >= 10:
                self.stdout.write(self.style.SUCCESS('✅ Database has sufficient data'))
                signal.alarm(0)  # Cancel timeout
                return
            
            # Create data if missing
            if candidates_count < 10:
                self.stdout.write(f'👥 Creating {10 - candidates_count} candidates...')
                self.create_candidates(10 - candidates_count)
            
            if jobs_count < 10:
                self.stdout.write(f'💼 Creating {10 - jobs_count} job listings...')
                self.create_jobs(10 - jobs_count)
            
            self.stdout.write(self.style.SUCCESS('✅ Sufficient data ensured!'))
            signal.alarm(0)  # Cancel timeout
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error ensuring data: {str(e)}'))
            signal.alarm(0)  # Cancel timeout
    
    def create_candidates(self, count):
        """Create multiple candidates quickly"""
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emma', 'James', 'Olivia', 'Robert', 'Sophia']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson', 'Moore']
        positions = ['Python Developer', 'React Developer', 'DevOps Engineer', 'Data Scientist', 'UI/UX Designer', 
                    'Full Stack Developer', 'Backend Developer', 'Frontend Developer', 'Mobile Developer', 'QA Engineer']
        
        # Get or create a location
        location, _ = Location.objects.get_or_create(country='Poland', city='Warsaw')
        
        created = 0
        for i in range(count):
            if self.timeout_occurred:
                break
                
            try:
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                email = f"{first_name.lower()}.{last_name.lower()}{i+1}@example.com"
                
                # Skip if user already exists
                if User.objects.filter(email=email).exists():
                    continue
                
                # Create User
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password='password123',
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create AppUser
                position = random.choice(positions)
                app_user = AppUser.objects.create(
                    user=user,
                    full_name=f'{first_name} {last_name}',
                    mobile=f'{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}',
                    position=position,
                    location=location,
                    role='worker',
                    about_me=f'I am a {position} with experience in modern technologies.'
                )
                
                # Add 3-5 random skills
                skills = list(Skill.objects.all())
                if skills:
                    num_skills = random.randint(3, min(5, len(skills)))
                    selected_skills = random.sample(skills, num_skills)
                    for skill in selected_skills:
                        UserSkill.objects.create(
                            user=app_user,
                            skill=skill,
                            level=random.randint(1, 3)
                        )
                
                created += 1
                self.stdout.write(f'✅ Created: {first_name} {last_name} - {position}')
                
            except Exception as e:
                self.stdout.write(f'❌ Failed to create candidate {i+1}: {str(e)}')
                continue
        
        self.stdout.write(f'👥 Created {created} candidates')
    
    def create_jobs(self, count):
        """Create multiple job listings quickly"""
        job_titles = ['Python Developer', 'React Developer', 'DevOps Engineer', 'Data Scientist', 'UI/UX Designer',
                     'Full Stack Developer', 'Backend Developer', 'Frontend Developer', 'Mobile Developer', 'QA Engineer']
        companies = ['TechCorp', 'WebSolutions', 'CloudTech', 'DataFlow', 'InnovateLab', 'DigitalDynamics', 
                    'CodeForge', 'PixelPerfect', 'AgileWorks', 'NextGen']
        
        # Get or create recruiters
        recruiters = []
        for i in range(3):  # Create 3 recruiters
            email = f'recruiter{i+1}@example.com'
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password='password123',
                    first_name=f'Recruiter{i+1}',
                    last_name='Smith'
                )
                app_user = AppUser.objects.create(
                    user=user,
                    full_name=f'Recruiter {i+1} Smith',
                    role='recruiter',
                    position='HR Manager'
                )
                recruiters.append(app_user)
            else:
                recruiters.append(User.objects.get(email=email).appuser)
        
        # Get or create a location
        location, _ = Location.objects.get_or_create(country='Poland', city='Warsaw')
        
        created = 0
        for i in range(count):
            if self.timeout_occurred:
                break
                
            try:
                job_title = random.choice(job_titles)
                company = random.choice(companies)
                recruiter = random.choice(recruiters)
                
                # Create job
                job = JobListing.objects.create(
                    job_title=job_title,
                    company_name=company,
                    about_company=f'{company} is a great company to work for',
                    job_description=f'We need an experienced {job_title} to join our team',
                    salary_min=random.randint(4000, 8000),
                    salary_max=random.randint(8000, 15000),
                    salary_currency='PLN',
                    location=location,
                    job_model=random.choice(['REMOTE', 'HYBRID', 'STATIONARY']),
                    owner=recruiter,
                    status='ACTIVE'
                )
                
                # Add 3-5 random skills
                skills = list(Skill.objects.all())
                if skills:
                    num_skills = random.randint(3, min(5, len(skills)))
                    selected_skills = random.sample(skills, num_skills)
                    for skill in selected_skills:
                        JobListingSkill.objects.create(
                            job_listing=job,
                            skill=skill,
                            level=random.randint(1, 5)
                        )
                
                created += 1
                self.stdout.write(f'✅ Created: {job_title} at {company}')
                
            except Exception as e:
                self.stdout.write(f'❌ Failed to create job {i+1}: {str(e)}')
                continue
        
        self.stdout.write(f'💼 Created {created} job listings')
