# Job.it - Job Board Platform with AI Features

A Django-based job board platform featuring AI-powered job matching, user management, and real-time chat functionality.

## 🚀 Quick Start (Docker - OS Independent)

### Prerequisites
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Git** to clone the repository

### Setup (Works on Any OS - No API Keys Required!)
```bash
# 1. Clone the repository
git clone <your-repository-url>
cd jobit

# 2. Start the application with Docker
docker-compose up --build

# 3. Access the application
# Main App: http://localhost:8000
# Admin Panel: http://localhost:8000/admin
# Default Login: admin / admin123
```

### Stop the Application
```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (clean slate)
docker-compose down -v
```

## 🎯 What Works Out of the Box

✅ **Complete Job Board**: User registration, job posting, applications  
✅ **User Management**: Login, profiles, authentication  
✅ **File Uploads**: Local file storage (no Azure required)  
✅ **Database**: SQLite database with sample data  
✅ **Admin Panel**: Full Django admin interface  
✅ **Responsive Design**: Mobile-friendly interface  

## 🔧 Optional: Enhanced Features

**To enable full functionality, create a `.env` file:**
```bash
# Copy the template
cp env.example .env

# Edit with your API keys (optional)
nano .env
```

**Enhanced features (optional):**
- **AI Job Matching**: Add `OPENAI_API_KEY`
- **Cloud File Storage**: Add `AZURE_STORAGE_CONNECTION_STRING`
- **Email Notifications**: Add `EMAIL_HOST_PASSWORD`

## 🔧 Alternative: Local Development

If you prefer to run without Docker:

#### Prerequisites
- Python 3.8+
- pip

#### Setup
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Start development server
python manage.py runserver
```

## 🏗️ Architecture

- **Backend**: Django 4.x with REST API
- **Database**: SQLite (default) / PostgreSQL (configurable)
- **Frontend**: Django Templates with modern CSS/JS
- **File Storage**: Local storage (default) / Azure Blob Storage (optional)
- **AI Features**: OpenAI integration (optional)
- **Authentication**: Django built-in user system

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file in the project root for enhanced features:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Optional: API Keys for enhanced functionality
OPENAI_API_KEY=your-openai-api-key
AZURE_STORAGE_CONNECTION_STRING=your-azure-connection-string
EMAIL_HOST_PASSWORD=your-gmail-app-password

# Database (optional - defaults to SQLite)
DB_NAME=jobit
DB_USER=jobit_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

## 📱 Features

- **User Management**: Registration, login, profiles
- **Job Posting**: Create and manage job listings
- **AI Matching**: Intelligent job-candidate matching (with OpenAI key)
- **Real-time Chat**: Communication between users
- **File Uploads**: Resume and profile photo uploads
- **Responsive Design**: Mobile-friendly interface

## 🐳 Docker Commands

### Basic Operations
```bash
# Start the application
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Rebuild and start
docker-compose up --build
```

### Development Commands
```bash
# Run Django commands inside container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Access container shell
docker-compose exec web bash

# View container status
docker-compose ps
```

### Troubleshooting
```bash
# Clean up everything
docker-compose down -v
docker system prune -f

# Check container logs
docker-compose logs web

# Restart specific service
docker-compose restart web
```

## 🧪 Testing

```bash
# Run tests in Docker
docker-compose exec web python manage.py test

# Run specific app tests
docker-compose exec web python manage.py test users
docker-compose exec web python manage.py test jobs
docker-compose exec web python manage.py test chat
```

## 📚 Documentation

- **Docker Setup**: See `docker-compose.yml` and `Dockerfile`
- **Docker Guide**: See `DOCKER_README.md` for detailed Docker instructions
- **Local Development**: See alternative setup above
- **API Documentation**: Available at `/api/` when running

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of an engineering thesis. All rights reserved.

## 🆘 Support

For issues and questions:
1. Check the existing issues
2. Create a new issue with detailed description
3. Include your environment details (Docker version, OS)

---

**Note**: This application is designed for educational and demonstration purposes. For production use, ensure proper security measures and environment configuration.

## 🎯 Why Docker?

- **OS Independent**: Works the same on Windows, Mac, and Linux
- **No Environment Setup**: No need to install Python, dependencies, or databases
- **Consistent**: Same environment for all developers
- **Easy Deployment**: Can be deployed anywhere Docker runs
- **Clean Isolation**: Doesn't interfere with your system's Python installation
- **Works Out of the Box**: No API keys required for basic functionality
