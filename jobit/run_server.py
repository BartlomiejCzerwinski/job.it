import os
import sys
import django
from django.core.management import call_command

def main():
    print("Starting server initialization...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobit.settings')
    print("Django settings module set")
    
    django.setup()
    print("Django setup complete")
    
    print("Starting location update process...")
    try:
        call_command('update_locations')
        print("Location update command completed")
    except Exception as e:
        print(f"Error updating locations: {str(e)}")
    
    print("Starting development server...")
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver'])

if __name__ == '__main__':
    print("Script started")
    main() 