from django.core.management.base import BaseCommand
from users.models import Skill
import csv
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Initialize skills from CSV file'

    def handle(self, *args, **options):
        # Check if skills already exist
        if Skill.objects.exists():
            self.stdout.write(
                self.style.WARNING('Skills already exist in database. Skipping initialization.')
            )
            return

        # Path to the skills CSV file
        csv_file_path = os.path.join(settings.BASE_DIR, 'skills.csv')
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(
                self.style.ERROR(f'Skills CSV file not found at: {csv_file_path}')
            )
            return

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                skills_created = 0
                
                for row in csv_reader:
                    if row and row[0].strip():  # Skip empty rows
                        skill_name = row[0].strip()
                        if not Skill.objects.filter(name=skill_name).exists():
                            Skill.objects.create(name=skill_name)
                            skills_created += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created {skills_created} skills from CSV')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading CSV file: {e}')
            )