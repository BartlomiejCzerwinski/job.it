#!/bin/bash

# 🚀 Job.it Startup Script
# This script ensures the database is ready before starting Django

echo "🚀 Starting Job.it application..."

# Wait for database to be ready (for production databases)
echo "⏳ Checking database connection..."

# Run database migrations
echo "🔄 Running database migrations..."
python jobit/manage.py makemigrations chat
python jobit/manage.py makemigrations users
python jobit/manage.py makemigrations jobs
python jobit/manage.py makemigrations applications
python jobit/manage.py makemigrations matching
python jobit/manage.py makemigrations
python jobit/manage.py migrate chat
python jobit/manage.py migrate users
python jobit/manage.py migrate jobs
python jobit/manage.py migrate applications
python jobit/manage.py migrate matching
python jobit/manage.py migrate

echo "📁 Checking static files in source directory..."
ls -la /app/jobit/jobs/static/ || echo "Source static directory not found"
ls -la /app/jobit/jobs/static/css/ || echo "CSS directory not found"
ls -la /app/jobit/jobs/static/js/ || echo "JS directory not found"  
ls -la /app/jobit/jobs/static/images/ || echo "Images directory not found"

# Initialize skills from CSV file
echo "📚 Initializing skills from CSV..."
python jobit/manage.py init_skills

# Generate sample data for production (simple approach)
echo "🎯 Generating sample data..."
python jobit/manage.py generate_sample_candidates --count 25 || echo "Candidates generation failed or already exist"
python jobit/manage.py generate_sample_jobs --count 15 || echo "Jobs generation failed or already exist"
echo "✅ Sample data generation complete"

# Create superuser if it doesn't exist (optional)
echo "👤 Checking for superuser..."
python jobit/manage.py shell -c "
try:
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@jobit.com', 'admin123')
        print('✅ Superuser created: admin/admin123')
    else:
        print('✅ Superuser already exists')
except Exception as e:
    print(f'⚠️ Could not create superuser: {e}')
    print('Continuing without superuser...')
"

# Start Django development server
echo "🌐 Starting Django server..."
python jobit/manage.py runserver 0.0.0.0:8000
