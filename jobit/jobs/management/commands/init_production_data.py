from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import AppUser
from jobs.models import JobListing


class Command(BaseCommand):
    help = 'Initialize production data (candidates and jobs) if database is empty'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force data generation even if data already exists'
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # Check if data already exists
        has_candidates = AppUser.objects.filter(role='worker').exists()
        has_jobs = JobListing.objects.exists()
        
        if not force and (has_candidates or has_jobs):
            self.stdout.write(
                self.style.WARNING('Database already contains data. Use --force to regenerate.')
            )
            return
        
        # Generate candidates
        if not has_candidates or force:
            self.stdout.write('👥 Generating sample candidates...')
            from django.core.management import call_command
            call_command('generate_sample_candidates', '--count', '25')
            self.stdout.write(self.style.SUCCESS('✅ Generated 25 sample candidates'))
        else:
            self.stdout.write('👥 Candidates already exist, skipping...')
        
        # Generate jobs
        if not has_jobs or force:
            self.stdout.write('💼 Generating sample job listings...')
            from django.core.management import call_command
            call_command('generate_sample_jobs', '--count', '15')
            self.stdout.write(self.style.SUCCESS('✅ Generated 15 sample job listings'))
        else:
            self.stdout.write('💼 Job listings already exist, skipping...')
        
        self.stdout.write(self.style.SUCCESS('🎉 Production data initialization complete!'))
