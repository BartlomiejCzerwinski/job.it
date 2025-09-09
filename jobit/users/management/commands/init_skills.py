from django.core.management.base import BaseCommand
import os
import pandas as pd
from users.models import Skill


class Command(BaseCommand):
    help = 'Initialize skills from CSV file'

    def handle(self, *args, **options):
        # Get the path to skills.csv
        file_path = os.path.join(os.path.dirname(__file__), "../../../skills.csv")
        
        try:
            # Check if skills already exist
            if Skill.objects.exists():
                self.stdout.write(
                    self.style.WARNING('Skills already exist in database. Skipping initialization.')
                )
                return
            
            # Read skills from CSV
            skills_data = pd.read_csv(file_path)
            
            # Create skills
            skills_created = 0
            for skill_name in skills_data["name"]:
                skill, created = Skill.objects.get_or_create(name=skill_name.strip())
                if created:
                    skills_created += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully initialized {skills_created} skills from CSV.')
            )
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Skills CSV file not found at: {file_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing skills: {str(e)}')
            )
