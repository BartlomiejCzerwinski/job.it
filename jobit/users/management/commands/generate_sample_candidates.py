from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import AppUser, Skill, UserSkill, Location, SocialLink, Project
import random
import json

class Command(BaseCommand):
    help = 'Generate sample candidate profiles for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of candidate profiles to create (default: 10)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing worker profiles before creating new ones'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Sample first and last names
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
        
        # Sample data for realistic profiles
        positions = [
            'Full Stack Developer',
            'Frontend Developer', 
            'Backend Developer',
            'Mobile Developer',
            'DevOps Engineer',
            'Data Scientist',
            'Machine Learning Engineer',
            'UI/UX Designer',
            'Software Engineer',
            'Cloud Architect',
            'QA Engineer',
            'Security Engineer',
            'Product Manager',
            'Scrum Master',
            'Business Analyst'
        ]
        
        about_me_templates = [
            "Passionate {position} with {years} years of experience in building scalable applications. I love working with modern technologies and solving complex problems.",
            "Experienced {position} specializing in {specialty}. I enjoy collaborating with teams and delivering high-quality solutions.",
            "{years}+ years as a {position}. Strong focus on clean code, best practices, and continuous learning.",
            "Creative and detail-oriented {position} with expertise in {specialty}. Always eager to take on new challenges.",
            "Results-driven {position} with a proven track record of delivering projects on time. Passionate about {specialty}.",
            "Dedicated {position} with strong problem-solving skills. I thrive in fast-paced environments and enjoy learning new technologies.",
            "Innovative {position} with {years} years of hands-on experience. Committed to writing efficient, maintainable code.",
            "Skilled {position} passionate about {specialty}. I believe in the power of technology to solve real-world problems."
        ]
        
        specialties = [
            'web development', 'mobile applications', 'cloud infrastructure', 
            'microservices', 'API design', 'database optimization',
            'machine learning', 'data visualization', 'DevOps practices',
            'agile methodologies', 'user experience', 'system architecture'
        ]
        
        project_templates = [
            {
                'title': 'E-commerce Platform',
                'description': 'Built a full-stack e-commerce platform with payment integration, inventory management, and real-time analytics dashboard.',
                'technologies': ['React', 'Node.js', 'MongoDB', 'Stripe API', 'Redux']
            },
            {
                'title': 'Task Management System',
                'description': 'Developed a collaborative task management application with real-time updates, team collaboration features, and reporting.',
                'technologies': ['Angular', 'Django', 'PostgreSQL', 'WebSocket', 'Docker']
            },
            {
                'title': 'Social Media Analytics Tool',
                'description': 'Created an analytics dashboard for social media metrics with data visualization and automated reporting features.',
                'technologies': ['Python', 'React', 'D3.js', 'Redis', 'Celery']
            },
            {
                'title': 'Mobile Banking App',
                'description': 'Developed a secure mobile banking application with biometric authentication and transaction management.',
                'technologies': ['React Native', 'Node.js', 'JWT', 'PostgreSQL', 'AWS']
            },
            {
                'title': 'AI Chatbot',
                'description': 'Built an intelligent chatbot using NLP for customer support with multi-language support.',
                'technologies': ['Python', 'TensorFlow', 'Flask', 'Docker', 'Redis']
            },
            {
                'title': 'Real-time Collaboration Tool',
                'description': 'Created a real-time collaboration platform for remote teams with video conferencing and document sharing.',
                'technologies': ['Vue.js', 'WebRTC', 'Node.js', 'Socket.io', 'MongoDB']
            },
            {
                'title': 'IoT Dashboard',
                'description': 'Developed a dashboard for monitoring and controlling IoT devices with real-time data visualization.',
                'technologies': ['React', 'MQTT', 'InfluxDB', 'Grafana', 'Python']
            },
            {
                'title': 'Content Management System',
                'description': 'Built a flexible CMS with custom plugins, multi-site support, and advanced SEO features.',
                'technologies': ['Django', 'Vue.js', 'PostgreSQL', 'Elasticsearch', 'Redis']
            }
        ]
        
        # Clear existing worker profiles if requested
        if options['clear']:
            self.stdout.write('Clearing existing worker profiles...')
            AppUser.objects.filter(role='worker').delete()
            # Also delete associated users
            User.objects.filter(appuser__role='worker').delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing worker profiles'))
        
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
        
        self.stdout.write(f'Creating {count} candidate profiles...')
        
        created_count = 0
        for i in range(count):
            try:
                # Create unique email
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@example.com"
                
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    continue
                
                # Create User
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password='password123',  # Default password for all test users
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create AppUser
                position = random.choice(positions)
                years = random.randint(1, 15)
                
                app_user = AppUser.objects.create(
                    user=user,
                    full_name=f"{first_name} {last_name}",
                    mobile=f"{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}",
                    position=position,
                    location=random.choice(locations),
                    is_remote=random.choice([True, False]),
                    is_hybrid=random.choice([True, False]),
                    starts_in=random.choice(['ASAP', '2 weeks', '1 month', '3 months']),
                    role='worker',
                    about_me=random.choice(about_me_templates).format(
                        position=position,
                        years=years,
                        specialty=random.choice(specialties)
                    )
                )
                
                # Add skills (5-12 random skills with different levels)
                num_skills = random.randint(5, 12)
                selected_skills = random.sample(skills, min(num_skills, len(skills)))
                
                for skill in selected_skills:
                    UserSkill.objects.create(
                        user=app_user,
                        skill=skill,
                        level=random.randint(1, 3)  # 1=Beginner, 2=Intermediate, 3=Advanced
                    )
                
                # Add social links (2-4 random links)
                num_links = random.randint(2, 4)
                platforms_used = []
                
                if 'github' not in platforms_used and random.choice([True, False]):
                    SocialLink.objects.create(
                        user=app_user,
                        platform='github',
                        url=f"https://github.com/{first_name.lower()}{last_name.lower()}",
                        display_name=f"{first_name} {last_name}"
                    )
                    platforms_used.append('github')
                
                if 'linkedin' not in platforms_used and random.choice([True, False]):
                    SocialLink.objects.create(
                        user=app_user,
                        platform='linkedin',
                        url=f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
                        display_name=f"{first_name} {last_name}"
                    )
                    platforms_used.append('linkedin')
                
                if 'website' not in platforms_used and random.choice([True, False]):
                    SocialLink.objects.create(
                        user=app_user,
                        platform='website',
                        url=f"https://{first_name.lower()}{last_name.lower()}.dev",
                        display_name=f"Personal Portfolio"
                    )
                    platforms_used.append('website')
                
                if 'stackoverflow' not in platforms_used and random.choice([True, False]):
                    SocialLink.objects.create(
                        user=app_user,
                        platform='stackoverflow',
                        url=f"https://stackoverflow.com/users/{random.randint(1000000, 9999999)}/{first_name.lower()}",
                        display_name=f"{first_name} {last_name}"
                    )
                    platforms_used.append('stackoverflow')
                
                # Add projects (1-3 random projects)
                num_projects = random.randint(1, 3)
                selected_projects = random.sample(project_templates, num_projects)
                
                for idx, project_data in enumerate(selected_projects):
                    project = Project.objects.create(
                        user=app_user,
                        title=project_data['title'],
                        description=project_data['description'],
                        technologies=json.dumps(project_data['technologies']),
                        github_link=f"https://github.com/{first_name.lower()}{last_name.lower()}/{project_data['title'].lower().replace(' ', '-')}" if random.choice([True, False]) else None,
                        demo_link=f"https://{project_data['title'].lower().replace(' ', '-')}.demo.com" if random.choice([True, False]) else None,
                        order=idx
                    )
                
                created_count += 1
                self.stdout.write(f"Created profile {created_count}/{count}: {email} - {position}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating profile: {str(e)}"))
                continue
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} candidate profiles!'))
        self.stdout.write(self.style.SUCCESS('All test users have password: password123'))
