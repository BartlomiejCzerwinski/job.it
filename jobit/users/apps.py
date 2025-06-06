import os
import pandas as pd
from django.apps import AppConfig
from django.db.utils import OperationalError
from django.db.models.signals import post_migrate
from .locations import LOCATIONS


def update_locations(sender, **kwargs):
    from .models import Location
    
    print("Starting location update process...")
    print(f"Number of locations in LOCATIONS dictionary: {sum(len(cities) for cities in LOCATIONS.values())}")
    
    existing_locations = set(
        (loc.country, loc.city) 
        for loc in Location.objects.all()
    )
    print(f"Number of existing locations in database: {len(existing_locations)}")
    
    new_locations_count = 0
    for country, cities in LOCATIONS.items():
        for city in cities:
            if (country, city) not in existing_locations:
                print(f"Creating new location: {country}, {city}")
                Location.objects.create(country=country, city=city)
                new_locations_count += 1
    
    print(f"Location update complete. Added {new_locations_count} new locations.")


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        print("UsersConfig ready method called")
        init_skills_table()
        # Connect the signal to update locations after migrations
        post_migrate.connect(update_locations, sender=self)
        print("post_migrate signal connected")


def init_skills_table():
    # Delayed import (after loading Django app)
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
