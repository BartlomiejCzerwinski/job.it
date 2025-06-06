from django.core.management.base import BaseCommand
from users.locations import LOCATIONS
from users.models import Location


class Command(BaseCommand):
    help = 'Updates locations in the database from the LOCATIONS dictionary'

    def handle(self, *args, **options):
        self.stdout.write("Starting location update process...")
        
        # Get existing locations
        existing_locations = set(
            (loc.country, loc.city) 
            for loc in Location.objects.all()
        )
        self.stdout.write(f"Found {len(existing_locations)} existing locations")
        
        # Check for new locations
        new_locations_count = 0
        for country, cities in LOCATIONS.items():
            for city in cities:
                if (country, city) not in existing_locations:
                    self.stdout.write(f"Creating new location: {country}, {city}")
                    Location.objects.create(country=country, city=city)
                    new_locations_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Successfully added {new_locations_count} new locations")) 