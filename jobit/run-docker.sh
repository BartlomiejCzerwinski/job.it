#!/bin/bash

# 🐳 Job.it Docker Runner Script
# This script helps you run your Docker application easily

echo "🚀 Starting Job.it Docker Application..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop or Docker daemon."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "📝 Created .env file from env.example"
        echo "🔐 Please edit .env file with your actual API keys and secrets"
        echo "   Then run this script again."
        exit 0
    else
        echo "❌ No env.example file found. Please create a .env file manually."
        exit 1
    fi
fi

echo "✅ Environment file found"

# Build and start the application
echo "🔨 Building and starting containers..."
docker-compose up --build -d

# Check if containers are running
if [ $? -eq 0 ]; then
    echo "✅ Application started successfully!"
    echo ""
    echo "🌐 Access your application at: http://localhost:8000"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:        docker-compose logs -f"
    echo "   Stop app:         docker-compose down"
    echo "   Restart app:      docker-compose restart"
    echo "   Check status:     docker-compose ps"
    echo "   Django shell:     docker-compose exec web python manage.py shell"
    echo "   Create superuser: docker-compose exec web python manage.py createsuperuser"
    echo ""
    echo "🔍 Checking container status..."
    docker-compose ps
else
    echo "❌ Failed to start application. Check logs with: docker-compose logs"
    exit 1
fi
