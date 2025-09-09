from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import AppUser, Skill, Location
from jobs.models import JobListing, JobListingSkill
import random
import json


class Command(BaseCommand):
    help = 'Generate sample job listings for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of job listings to create (default: 20)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing job listings before creating new ones'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Sample job titles
        job_titles = [
            'Senior Python Developer',
            'Full Stack Developer',
            'Frontend React Developer',
            'Backend Node.js Developer',
            'DevOps Engineer',
            'Data Scientist',
            'Machine Learning Engineer',
            'Mobile App Developer',
            'UI/UX Designer',
            'Cloud Architect',
            'QA Engineer',
            'Security Engineer',
            'Product Manager',
            'Scrum Master',
            'Business Analyst',
            'Software Engineer',
            'Java Developer',
            'C# Developer',
            'PHP Developer',
            'Ruby on Rails Developer',
            'Vue.js Developer',
            'Angular Developer',
            'Flutter Developer',
            'iOS Developer',
            'Android Developer',
            'Blockchain Developer',
            'Game Developer',
            'Embedded Systems Engineer',
            'System Administrator',
            'Database Administrator'
        ]
        
        # Sample company names
        company_names = [
            'TechCorp Solutions',
            'InnovateLab',
            'Digital Dynamics',
            'CloudTech Systems',
            'DataFlow Inc',
            'WebCraft Studios',
            'CodeForge Technologies',
            'PixelPerfect Design',
            'AgileWorks',
            'NextGen Software',
            'CyberShield Security',
            'AI Innovations',
            'MobileFirst Apps',
            'CloudScale Solutions',
            'DevOps Masters',
            'FullStack Pro',
            'ReactNative Experts',
            'Python Pioneers',
            'JavaScript Junction',
            'Database Dynamics',
            'API Architects',
            'Microservices Masters',
            'Container Kings',
            'Kubernetes Experts',
            'Docker Dynamics',
            'AWS Specialists',
            'Azure Advisors',
            'GCP Gurus',
            'Blockchain Builders',
            'IoT Innovators'
        ]
        
        # Sample company descriptions
        company_descriptions = [
            "We are a fast-growing tech startup focused on innovative solutions and cutting-edge technology.",
            "A leading software company with over 10 years of experience in delivering high-quality products.",
            "We're a team of passionate developers building the next generation of web applications.",
            "A dynamic company specializing in cloud solutions and digital transformation.",
            "We create innovative software solutions that help businesses grow and succeed.",
            "A technology company focused on AI, machine learning, and data science solutions.",
            "We're building the future of mobile applications with cutting-edge technology.",
            "A company dedicated to creating user-friendly and accessible software solutions.",
            "We specialize in enterprise software solutions and digital transformation.",
            "A tech company focused on cybersecurity and data protection solutions.",
            "We're passionate about open-source software and community-driven development.",
            "A company that combines creativity with technology to build amazing products.",
            "We specialize in e-commerce solutions and online marketplace platforms.",
            "A technology company focused on IoT and smart device solutions.",
            "We're building scalable and reliable software for the modern web.",
            "A company dedicated to creating inclusive and accessible technology solutions.",
            "We specialize in real-time applications and live streaming technology.",
            "A tech company focused on blockchain and cryptocurrency solutions.",
            "We're passionate about clean code, best practices, and continuous learning.",
            "A company that values innovation, collaboration, and professional growth."
        ]
        
        # Sample job descriptions
        job_descriptions = [
            "We are looking for a talented {position} to join our dynamic team. You will work on exciting projects using modern technologies and have the opportunity to grow your skills.",
            "Join our team as a {position} and help us build innovative solutions. We offer a collaborative environment, competitive salary, and great benefits.",
            "We need a skilled {position} to work on our latest projects. You'll be part of a creative team that values innovation and quality.",
            "Looking for an experienced {position} to join our growing team. You'll work with cutting-edge technology and have opportunities for career advancement.",
            "We're seeking a passionate {position} to help us build the next generation of software solutions. Join our team and make a real impact.",
            "Come work with us as a {position} and be part of something amazing. We offer flexible working arrangements and a supportive team environment.",
            "We need a talented {position} to join our team of experts. You'll work on challenging projects and have access to the latest tools and technologies.",
            "Join our company as a {position} and help us create innovative solutions. We value creativity, collaboration, and continuous learning.",
            "We're looking for a skilled {position} to work on our exciting projects. You'll be part of a team that values quality and innovation.",
            "Come join our team as a {position} and help us build amazing software. We offer competitive compensation and a great work environment."
        ]
        
        # Sample skills combinations for different roles
        skill_combinations = {
            'Python Developer': ['Python', 'Django', 'Flask', 'PostgreSQL', 'Git'],
            'Full Stack Developer': ['JavaScript', 'React', 'Node.js', 'MongoDB', 'Express'],
            'Frontend Developer': ['JavaScript', 'React', 'Vue.js', 'HTML', 'CSS'],
            'Backend Developer': ['Python', 'Django', 'PostgreSQL', 'Redis', 'Docker'],
            'DevOps Engineer': ['Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Linux'],
            'Data Scientist': ['Python', 'Pandas', 'NumPy', 'Scikit-learn', 'Jupyter'],
            'Mobile Developer': ['React Native', 'JavaScript', 'iOS', 'Android', 'Git'],
            'UI/UX Designer': ['Figma', 'Adobe XD', 'Sketch', 'HTML', 'CSS'],
            'Cloud Architect': ['AWS', 'Azure', 'Docker', 'Kubernetes', 'Terraform'],
            'QA Engineer': ['Selenium', 'Python', 'Jest', 'Cypress', 'Git']
        }
        
        # Clear existing job listings if requested
        if options['clear']:
            self.stdout.write('Clearing existing job listings...')
            JobListing.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing job listings'))
        
        # Get all available skills
        skills = list(Skill.objects.all())
        if not skills:
            self.stdout.write(self.style.ERROR('No skills found in database. Please load skills first.'))
            return
        
        # Get or create locations
        locations_data = [
            ('Poland', 'Warsaw'),
            ('Poland', 'Krakow'),
            ('Poland', 'Wroclaw'),
            ('Poland', 'Poznan'),
            ('Poland', 'Gdansk'),
            ('Germany', 'Berlin'),
            ('Germany', 'Munich'),
            ('Germany', 'Hamburg'),
            ('United Kingdom', 'London'),
            ('United Kingdom', 'Manchester'),
            ('United States', 'New York'),
            ('United States', 'San Francisco'),
            ('Netherlands', 'Amsterdam'),
            ('France', 'Paris'),
            ('Spain', 'Barcelona'),
            ('Spain', 'Madrid'),
            ('Italy', 'Milan'),
            ('Italy', 'Rome'),
            ('Sweden', 'Stockholm'),
            ('Norway', 'Oslo')
        ]
        
        locations = []
        for country, city in locations_data:
            location, _ = Location.objects.get_or_create(country=country, city=city)
            locations.append(location)
        
        # Get or create recruiter users
        recruiters = []
        for i in range(5):  # Create 5 recruiter accounts
            email = f"recruiter{i+1}@example.com"
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
                    position='HR Manager',
                    mobile=f"{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"
                )
                recruiters.append(app_user)
            else:
                user = User.objects.get(email=email)
                app_user = user.appuser
                recruiters.append(app_user)
        
        self.stdout.write(f'Creating {count} job listings...')
        
        created_count = 0
        for i in range(count):
            try:
                # Select random job title and company
                job_title = random.choice(job_titles)
                company_name = random.choice(company_names)
                
                # Generate salary based on job title
                if 'Senior' in job_title or 'Lead' in job_title:
                    salary_min = random.randint(8000, 15000)
                    salary_max = random.randint(15000, 25000)
                elif 'Junior' in job_title or 'Entry' in job_title:
                    salary_min = random.randint(3000, 6000)
                    salary_max = random.randint(6000, 10000)
                else:
                    salary_min = random.randint(5000, 10000)
                    salary_max = random.randint(10000, 18000)
                
                # Select currency based on location
                location = random.choice(locations)
                if location.country in ['Poland']:
                    currency = 'PLN'
                elif location.country in ['Germany', 'France', 'Spain', 'Italy', 'Netherlands', 'Sweden', 'Norway']:
                    currency = 'EUR'
                else:
                    currency = 'USD'
                
                # Create job listing
                job_listing = JobListing.objects.create(
                    job_title=job_title,
                    company_name=company_name,
                    about_company=random.choice(company_descriptions),
                    job_description=random.choice(job_descriptions).format(position=job_title),
                    salary_min=salary_min,
                    salary_max=salary_max,
                    salary_currency=currency,
                    location=location,
                    job_model=random.choice(['STATIONARY', 'HYBRID', 'REMOTE']),
                    owner=random.choice(recruiters),
                    status=random.choice(['ACTIVE', 'ACTIVE', 'ACTIVE', 'CLOSED'])  # 75% active
                )
                
                # Add skills to job listing
                # Try to get skills from predefined combinations first
                job_skills = []
                for role, role_skills in skill_combinations.items():
                    if any(keyword in job_title.lower() for keyword in role.lower().split()):
                        job_skills = role_skills
                        break
                
                # If no predefined combination, select random skills
                if not job_skills:
                    num_skills = random.randint(3, 8)
                    job_skills = random.sample([skill.name for skill in skills], min(num_skills, len(skills)))
                
                # Add skills to job listing
                for skill_name in job_skills:
                    try:
                        skill = Skill.objects.get(name=skill_name)
                        JobListingSkill.objects.create(
                            job_listing=job_listing,
                            skill=skill,
                            level=random.randint(1, 5)  # 1-5 skill level
                        )
                    except Skill.DoesNotExist:
                        continue
                
                created_count += 1
                self.stdout.write(f"Created job {created_count}/{count}: {job_title} at {company_name}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating job listing: {str(e)}"))
                continue
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} job listings!'))
        self.stdout.write(self.style.SUCCESS('All recruiter accounts have password: password123'))
