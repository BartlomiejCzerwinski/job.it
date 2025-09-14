from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import AppUser, Skill, UserSkill, Location, SocialLink, Project
from jobs.models import JobListing, JobListingSkill
import random
import json
from users.locations import LOCATIONS

class Command(BaseCommand):
    help = 'Generate comprehensive sample data including job listings and user profiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--job-count',
            type=int,
            default=15,
            help='Number of job listings to create (default: 15)'
        )
        parser.add_argument(
            '--user-count',
            type=int,
            default=5,
            help='Number of user profiles to create (default: 5)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new ones'
        )

    def handle(self, *args, **options):
        job_count = options['job_count']
        user_count = options['user_count']
        
        if options['clear']:
            self.stdout.write('🗑️ Clearing existing data...')
            JobListing.objects.all().delete()
            AppUser.objects.filter(role=AppUser.WORKER).delete()
            User.objects.filter(appuser__role=AppUser.WORKER).delete()
            self.stdout.write('✅ Existing data cleared')

        # Ensure locations exist
        self.ensure_locations()
        
        # Generate job listings
        self.generate_job_listings(job_count)
        
        # Generate user profiles
        self.generate_user_profiles(user_count)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully created {job_count} job listings and {user_count} user profiles!')
        )

    def ensure_locations(self):
        """Create Location objects from the predefined locations"""
        created_count = 0
        for country, cities in LOCATIONS.items():
            for city in cities:
                location, created = Location.objects.get_or_create(
                    country=country,
                    city=city
                )
                if created:
                    created_count += 1
        
        if created_count > 0:
            self.stdout.write(f'📍 Created {created_count} new locations')

    def generate_job_listings(self, count):
        """Generate realistic job listings"""
        self.stdout.write(f'💼 Creating {count} job listings...')
        
        # Job data
        job_titles = [
            'Senior Python Developer', 'Full Stack Developer', 'React Frontend Developer',
            'Backend Engineer', 'DevOps Engineer', 'Data Scientist', 'Machine Learning Engineer',
            'Cloud Architect', 'Mobile App Developer', 'UI/UX Designer', 'Product Manager',
            'Software Engineer', 'Java Developer', 'Node.js Developer', 'Django Developer',
            'Flask Developer', 'Angular Developer', 'Vue.js Developer', 'iOS Developer',
            'Android Developer', 'Blockchain Developer', 'Cybersecurity Specialist',
            'Database Administrator', 'System Administrator', 'QA Engineer',
            'Technical Writer', 'Solutions Architect', 'Team Lead', 'Scrum Master',
            'Business Analyst', 'Data Analyst', 'Frontend Architect', 'Backend Architect'
        ]
        
        companies = [
            'TechCorp Solutions', 'InnovateLab', 'Digital Dynamics', 'CloudTech Systems',
            'DataFlow Inc', 'WebCraft Studios', 'MobileFirst', 'AI Innovations',
            'CyberSecure Ltd', 'DevOps Pro', 'CodeCrafters', 'FutureTech',
            'SmartSolutions', 'NextGen Software', 'AgileWorks', 'ScaleUp Technologies',
            'InnovationHub', 'TechPioneers', 'DigitalWorks', 'CloudFirst',
            'DataDriven Inc', 'WebWizards', 'MobileMasters', 'AITech Solutions',
            'SecureCode', 'DevOps Masters', 'CodeGenius', 'FutureWorks',
            'SmartTech', 'NextLevel', 'AgileTech', 'ScaleUp'
        ]
        
        about_companies = [
            "We are a fast-growing technology company focused on innovative solutions and cutting-edge development.",
            "Our company specializes in digital transformation and modern software development practices.",
            "We're a team of passionate developers building the next generation of web applications.",
            "A leading technology firm committed to excellence in software development and user experience.",
            "We create innovative solutions that help businesses scale and grow in the digital age.",
            "Our mission is to deliver high-quality software products that make a real difference.",
            "We're a dynamic startup focused on AI and machine learning solutions.",
            "A technology company dedicated to building scalable and maintainable software systems.",
            "We specialize in cloud-native applications and modern development methodologies.",
            "Our team is passionate about creating user-friendly and efficient software solutions."
        ]
        
        job_descriptions = [
            "We are looking for a talented developer to join our team and work on exciting projects using modern technologies.",
            "Join our dynamic team and contribute to building scalable applications that serve millions of users.",
            "We need a skilled professional who can design and implement robust software solutions.",
            "Looking for someone passionate about clean code and best practices in software development.",
            "We offer the opportunity to work with cutting-edge technologies and grow your career.",
            "Join our team and help us build innovative solutions that solve real-world problems.",
            "We're seeking a developer who can work independently and collaborate effectively with our team.",
            "Looking for someone with strong problem-solving skills and a passion for technology.",
            "We offer a challenging environment where you can learn and grow as a developer.",
            "Join our team and work on projects that have a real impact on our users and business."
        ]
        
        # Get all locations and skills
        locations = list(Location.objects.all())
        skills = list(Skill.objects.all())
        
        if not locations:
            self.stdout.write(self.style.ERROR('No locations found. Please run migrations first.'))
            return
            
        if not skills:
            self.stdout.write(self.style.ERROR('No skills found. Please run init_skills command first.'))
            return

        for i in range(count):
            # Create job listing
            job_title = random.choice(job_titles)
            company_name = random.choice(companies)
            location = random.choice(locations)
            
            # Generate salary range based on job title
            if 'Senior' in job_title or 'Lead' in job_title or 'Architect' in job_title:
                salary_min = random.randint(8000, 15000)
                salary_max = salary_min + random.randint(3000, 7000)
            elif 'Junior' in job_title or 'Intern' in job_title:
                salary_min = random.randint(3000, 6000)
                salary_max = salary_min + random.randint(1000, 2000)
            else:
                salary_min = random.randint(5000, 10000)
                salary_max = salary_min + random.randint(2000, 4000)
            
            job_listing = JobListing.objects.create(
                job_title=job_title,
                company_name=company_name,
                about_company=random.choice(about_companies),
                job_description=random.choice(job_descriptions),
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency=random.choice(['PLN', 'EUR', 'USD']),
                location=location,
                job_model=random.choice(['STATIONARY', 'HYBRID', 'REMOTE']),
                status='ACTIVE'
            )
            
            # Add skills to job listing
            job_skills = random.sample(skills, random.randint(3, 8))
            for skill in job_skills:
                JobListingSkill.objects.create(
                    job_listing=job_listing,
                    skill=skill,
                    level=random.randint(1, 5)
                )
            
            self.stdout.write(f'✅ Created: {job_title} at {company_name}')

    def generate_user_profiles(self, count):
        """Generate realistic user profiles"""
        self.stdout.write(f'👤 Creating {count} user profiles...')
        
        # User data
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'James', 'Olivia',
            'Robert', 'Sophia', 'William', 'Isabella', 'Richard', 'Mia', 'Joseph',
            'Charlotte', 'Thomas', 'Amelia', 'Charles', 'Harper', 'Christopher', 'Evelyn',
            'Daniel', 'Abigail', 'Matthew', 'Emily', 'Anthony', 'Elizabeth', 'Mark', 'Sofia',
            'Paul', 'Avery', 'Steven', 'Ella', 'Andrew', 'Madison', 'Kenneth', 'Scarlett',
            'Joshua', 'Victoria', 'Kevin', 'Aria', 'Brian', 'Grace', 'George', 'Chloe'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
            'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
            'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
            'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill',
            'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell'
        ]
        
        positions = [
            'Full Stack Developer', 'Frontend Developer', 'Backend Developer', 'Mobile Developer',
            'DevOps Engineer', 'Data Scientist', 'Machine Learning Engineer', 'UI/UX Designer',
            'Product Manager', 'Software Engineer', 'Java Developer', 'Python Developer',
            'React Developer', 'Node.js Developer', 'Django Developer', 'Flask Developer',
            'Angular Developer', 'Vue.js Developer', 'iOS Developer', 'Android Developer',
            'Blockchain Developer', 'Cybersecurity Specialist', 'Database Administrator',
            'System Administrator', 'QA Engineer', 'Technical Writer', 'Solutions Architect',
            'Team Lead', 'Scrum Master', 'Business Analyst', 'Data Analyst'
        ]
        
        about_me_templates = [
            "Passionate developer with {years} years of experience in {technologies}. I love building scalable applications and solving complex problems.",
            "Experienced {position} with a strong background in {technologies}. Always eager to learn new technologies and take on new challenges.",
            "Dedicated software professional with expertise in {technologies}. I enjoy working in collaborative environments and contributing to meaningful projects.",
            "Skilled {position} with {years} years of experience. Passionate about clean code, best practices, and continuous learning.",
            "Experienced developer specializing in {technologies}. I have a strong track record of delivering high-quality software solutions.",
            "Passionate about technology and innovation. With {years} years of experience in {technologies}, I bring both technical skills and creative problem-solving.",
            "Dedicated {position} with expertise in {technologies}. I enjoy working on challenging projects and contributing to team success.",
            "Experienced software professional with a passion for {technologies}. I believe in writing clean, maintainable code and following best practices."
        ]
        
        # Get all locations and skills
        locations = list(Location.objects.all())
        skills = list(Skill.objects.all())
        
        if not locations:
            self.stdout.write(self.style.ERROR('No locations found. Please run migrations first.'))
            return
            
        if not skills:
            self.stdout.write(self.style.ERROR('No skills found. Please run init_skills command first.'))
            return

        for i in range(count):
            # Generate user data
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(100, 999)}@example.com"
            position = random.choice(positions)
            location = random.choice(locations)
            
            # Create Django User
            user = User.objects.create_user(
                username=email,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name
            )
            
            # Create AppUser profile
            years_experience = random.randint(1, 10)
            user_skills = random.sample(skills, random.randint(5, 12))
            technologies = ', '.join([skill.name for skill in user_skills[:5]])
            
            about_me = random.choice(about_me_templates).format(
                years=years_experience,
                technologies=technologies,
                position=position
            )
            
            app_user = AppUser.objects.create(
                user=user,
                about_me=about_me,
                full_name=f"{first_name} {last_name}",
                mobile=f"+48{random.randint(100000000, 999999999)}",
                position=position,
                location=location,
                is_remote=random.choice([True, False]),
                is_hybrid=random.choice([True, False]),
                starts_in=random.choice(['ASAP', '2 weeks', '1 month', '3 months']),
                role=AppUser.WORKER
            )
            
            # Add skills to user
            for skill in user_skills:
                UserSkill.objects.create(
                    user=app_user,
                    skill=skill,
                    level=random.randint(1, 5)
                )
            
            # Add social links
            self.add_social_links(app_user)
            
            # Add projects
            self.add_projects(app_user, user_skills)
            
            self.stdout.write(f'✅ Created: {first_name} {last_name} - {position}')

    def add_social_links(self, app_user):
        """Add realistic social links to user profile"""
        social_platforms = [
            ('github', 'https://github.com/{}'),
            ('linkedin', 'https://linkedin.com/in/{}'),
            ('website', 'https://{}.dev'),
        ]
        
        # Add 1-3 social links
        num_links = random.randint(1, 3)
        selected_platforms = random.sample(social_platforms, num_links)
        
        for platform, url_template in selected_platforms:
            username = app_user.user.username.split('@')[0]
            url = url_template.format(username)
            
            SocialLink.objects.create(
                user=app_user,
                platform=platform,
                url=url,
                display_name=f"{app_user.user.first_name}'s {platform.title()}"
            )

    def add_projects(self, app_user, user_skills):
        """Add realistic projects to user profile"""
        project_templates = [
            {
                'title': 'E-commerce Platform',
                'description': 'Full-stack e-commerce application with user authentication, payment processing, and admin dashboard.',
                'technologies': ['React', 'Node.js', 'MongoDB', 'Stripe API']
            },
            {
                'title': 'Task Management App',
                'description': 'Collaborative task management tool with real-time updates and team collaboration features.',
                'technologies': ['Vue.js', 'Django', 'PostgreSQL', 'WebSockets']
            },
            {
                'title': 'Weather Dashboard',
                'description': 'Real-time weather monitoring dashboard with data visualization and location-based forecasts.',
                'technologies': ['React', 'Python', 'OpenWeather API', 'Chart.js']
            },
            {
                'title': 'Social Media Analytics',
                'description': 'Analytics platform for social media metrics with data processing and visualization.',
                'technologies': ['Angular', 'Python', 'Pandas', 'D3.js']
            },
            {
                'title': 'Mobile Banking App',
                'description': 'Secure mobile banking application with biometric authentication and transaction management.',
                'technologies': ['React Native', 'Node.js', 'PostgreSQL', 'JWT']
            },
            {
                'title': 'Machine Learning Model',
                'description': 'Predictive analytics model for customer behavior analysis with real-time scoring.',
                'technologies': ['Python', 'TensorFlow', 'Pandas', 'Flask']
            },
            {
                'title': 'API Gateway',
                'description': 'Microservices API gateway with authentication, rate limiting, and monitoring.',
                'technologies': ['Node.js', 'Express', 'Redis', 'Docker']
            },
            {
                'title': 'Data Visualization Tool',
                'description': 'Interactive data visualization platform with drag-and-drop chart creation.',
                'technologies': ['React', 'D3.js', 'Python', 'FastAPI']
            }
        ]
        
        num_projects = random.randint(2, 4)
        selected_projects = random.sample(project_templates, num_projects)
        
        for i, project_data in enumerate(selected_projects):
            available_skills = [skill.name for skill in user_skills]
            project_technologies = []
            
            for tech in project_data['technologies']:
                if tech in available_skills:
                    project_technologies.append(tech)
                elif random.random() < 0.3:  # 30% chance to include even if not in skills
                    project_technologies.append(tech)
            
            if not project_technologies:
                project_technologies = project_data['technologies'][:2]  # Fallback
            
            Project.objects.create(
                user=app_user,
                title=project_data['title'],
                description=project_data['description'],
                technologies=json.dumps(project_technologies),
                github_link=f"https://github.com/{app_user.user.username.split('@')[0]}/{project_data['title'].lower().replace(' ', '-')}",
                demo_link=f"https://{project_data['title'].lower().replace(' ', '-')}.demo.com" if random.random() < 0.7 else None,
                order=i
            )
