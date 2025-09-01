# 🐳 Running Job.it with Docker

## Quick Start

### 1. Install Docker
- **Windows/Mac**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: Install [Docker Engine](https://docs.docker.com/engine/install/)

### 2. Clone and Run
```bash
# Clone the repository
git clone https://github.com/BartlomiejCzerwinski/job.it/tree/local-setup
# Set to local setup branch
git checkout local-setup
cd jobit

# Start the application
docker-compose up --build
```

### 3. Access  App
- **Main Application**: http://localhost:8000

## 🎯 What Works Out of the Box

✅ **Complete Job Board**: User registration, job posting, applications  
✅ **User Management**: Login, profiles, authentication  
✅ **File Uploads**: Local file storage (no Azure integration required)  
✅ **Database**: SQLite database with sample data  
✅ **Responsive Design**: Mobile-friendly interface  
✅ **No API Keys Required**: Everything works immediately  