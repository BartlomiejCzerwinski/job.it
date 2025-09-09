from django.core.management.base import BaseCommand
from users.models import AppUser
from jobs.models import JobListing


class Command(BaseCommand):
    help = 'Check if database has sample data'

    def handle(self, *args, **options):
        try:
            candidates_count = AppUser.objects.filter(role='worker').count()
            jobs_count = JobListing.objects.count()
            
            self.stdout.write(f'Candidates: {candidates_count}')
            self.stdout.write(f'Job listings: {jobs_count}')
            
            if candidates_count > 5 and jobs_count > 5:
                self.stdout.write(self.style.SUCCESS('✅ Database has sample data'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Database is missing sample data'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error checking data: {str(e)}'))
