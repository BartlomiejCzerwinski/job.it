# 💼 job.it – Intelligent Recruitment Platform for IT

**job.it** is a modular web application designed to support and streamline the recruitment process in the IT industry. The platform connects job seekers and employers, offering tools for job searching, applications, communication, and intelligent job matching based on user profiles.

---

## 🗺️ System Architecture

The application follows a modular, scalable architecture built with Django. Each core functionality is implemented as a separate Django app to ensure maintainability and clarity.

![Applications-Diagram](https://github.com/user-attachments/assets/6fba49a9-da47-4db6-9fb0-f52ea53d2b30)

*The above diagram shows a high-level system architecture with separate modules for users, job offers, matching engine, and messaging.*

---

## 🧩 Component Diagram

The following diagram illustrates how the internal components of the system interact:

![Components-Diagram](https://github.com/user-attachments/assets/33bf8c30-0c24-40b9-bd8f-1bea2f745baf)

*Each component is responsible for a distinct area of functionality, such as user management, job posting, or chat messaging.*

---

## 🗃️ Database Schema

This relational model outlines how the core entities relate to one another:

<img width="698" height="690" alt="database" src="https://github.com/user-attachments/assets/0b58fbdc-fc58-4424-bcfc-d9eac83ae136" />

*The database schema supports users, job applications, communication logs, job offers, and matching metadata.*

---

## 🧠 Main Modules

- **Users** – Registration, authentication, session management, profile handling
- **Jobs** – Creating, editing, browsing, and managing job offers
- **Applications** – Job application submission, status tracking, and feedback
- **Messaging (Chat)** – Real-time communication between users
- **Matching** – AI-driven recommendation engine using user profiles and job data

---

## 🚀 Getting Started


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
