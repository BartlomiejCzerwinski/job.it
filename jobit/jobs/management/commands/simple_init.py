from django.core.management.base import BaseCommand
from users.models import AppUser, Skill, Location, UserSkill
from jobs.models import JobListing, JobListingSkill
from django.contrib.auth.models import User
import random


class Command(BaseCommand):
    help = 'Simple data initialization - creates 5 candidates and 5 jobs quickly'

    def handle(self, *args, **options):
        try:
            # Check current data
            candidates_count = AppUser.objects.filter(role='worker').count()
            jobs_count = JobListing.objects.count()
            
            self.stdout.write(f'📊 Current data: {candidates_count} candidates, {jobs_count} jobs')
            
            # Create 5 candidates if we have less than 5
            if candidates_count < 5:
                self.stdout.write('👥 Creating 5 candidates...')
                self.create_simple_candidates(5 - candidates_count)
            
            # Create 5 jobs if we have less than 5
            if jobs_count < 5:
                self.stdout.write('💼 Creating 5 job listings...')
                self.create_simple_jobs(5 - jobs_count)
            
            self.stdout.write(self.style.SUCCESS('✅ Simple data initialization complete!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error in simple init: {str(e)}'))
    
    def create_simple_candidates(self, count):
        """Create simple candidates quickly"""
        names = [
            ('John', 'Smith', 'Python Developer'),
            ('Jane', 'Doe', 'React Developer'),
            ('Mike', 'Johnson', 'DevOps Engineer'),
            ('Sarah', 'Wilson', 'Data Scientist'),
            ('David', 'Brown', 'Full Stack Developer')
        ]
        
        # Get or create a location
        location, _ = Location.objects.get_or_create(country='Poland', city='Warsaw')
        
        created = 0
        for i, (first_name, last_name, position) in enumerate(names[:count]):
            try:
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
                app_user = AppUser.objects.create(
                    user=user,
                    full_name=f'{first_name} {last_name}',
                    mobile=f'{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}',
                    position=position,
                    location=location,
                    role='worker',
                    about_me=f'I am a {position} with experience in modern technologies.'
                )
                
                # Add 2-3 random skills
                skills = list(Skill.objects.all())
                if skills:
                    num_skills = min(3, len(skills))
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
    
    def create_simple_jobs(self, count):
        """Create simple job listings quickly"""
        jobs = [
            ('Python Developer', 'TechCorp'),
            ('React Developer', 'WebSolutions'),
            ('DevOps Engineer', 'CloudTech'),
            ('Data Scientist', 'DataFlow'),
            ('Full Stack Developer', 'InnovateLab')
        ]
        
        # Get or create a recruiter
        email = 'recruiter@example.com'
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                username=email,
                email=email,
                password='password123',
                first_name='Recruiter',
                last_name='Smith'
            )
            recruiter = AppUser.objects.create(
                user=user,
                full_name='Recruiter Smith',
                role='recruiter',
                position='HR Manager'
            )
        else:
            recruiter = User.objects.get(email=email).appuser
        
        # Get or create a location
        location, _ = Location.objects.get_or_create(country='Poland', city='Warsaw')
        
        created = 0
        for i, (job_title, company) in enumerate(jobs[:count]):
            try:
                # Create job
                job = JobListing.objects.create(
                    job_title=job_title,
                    company_name=company,
                    about_company=f'{company} is a great company to work for',
                    job_description=f'We need an experienced {job_title} to join our team',
                    salary_min=random.randint(5000, 8000),
                    salary_max=random.randint(8000, 12000),
                    salary_currency='PLN',
                    location=location,
                    job_model=random.choice(['REMOTE', 'HYBRID', 'STATIONARY']),
                    owner=recruiter,
                    status='ACTIVE'
                )
                
                # Add 2-3 random skills
                skills = list(Skill.objects.all())
                if skills:
                    num_skills = min(3, len(skills))
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
