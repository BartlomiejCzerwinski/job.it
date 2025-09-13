import os
import pandas as pd
from django.apps import AppConfig
from django.db.utils import OperationalError
from django.db.models.signals import post_migrate
from .locations import LOCATIONS


def update_locations(sender, **kwargs):
    from .models import Location
    
    print("Checking for new locations...")
    
    try:
        # Get all existing locations from database
        existing_locations = set(
            (loc.country, loc.city) 
            for loc in Location.objects.all()
        )
        
        # Check all locations from LOCATIONS dictionary
        new_locations_count = 0
        for country, cities in LOCATIONS.items():
            for city in cities:
                if (country, city) not in existing_locations:
                    Location.objects.create(country=country, city=city)
                    new_locations_count += 1
        
        if new_locations_count > 0:
            print(f"Added {new_locations_count} new locations to database")
    except OperationalError:
        print("Database not ready yet, skipping location update")


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        post_migrate.connect(update_locations, sender=self)


def init_skills_table():
    from users.models import Skill

    file_path = os.path.join(os.path.dirname(__file__), "../skills.csv")

    try:
        any_skill = Skill.objects.all()[0]
    except IndexError:
        try:
            skills_data = pd.read_csv(file_path)
            for skill in skills_data["name"]:
                new_skill = Skill.objects.create(name=skill)
                new_skill.save()
        except OperationalError:
            print("Error during database init operation")
    except OperationalError:
        pass
