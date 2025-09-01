# 💼 job.it – Intelligent Recruitment Platform for IT

**job.it** is a modular web application designed to support and streamline the recruitment process in the IT industry. The platform connects job seekers and employers, offering tools for job searching, applications, communication, and intelligent job matching based on user profiles.

---

## 📸 Preview

### 🔑 Login
<img width="1920" height="919" alt="jobit_logowanie" src="https://github.com/user-attachments/assets/543fbd5d-c7e3-44df-907e-d763c285cc7b" />

*Simple login page for accessing the platform.*

---

### 👤 User Profile
<img width="1920" height="919" alt="jobit_panel" src="https://github.com/user-attachments/assets/c34147c9-9949-4a0c-b729-1512904d6683" />

*Editable user profile with personal information, skills, projects, and social links.*

---

### 🏠 Dashboard with AI Assistant
<img width="1920" height="878" alt="jobit_ai" src="https://github.com/user-attachments/assets/07ebde34-cf90-4287-997f-e4b15d2673f7" />

*Personalized job recommendations and search assistance powered by AI.*

---

### 💼 Job Listing & Applications
<img width="1920" height="919" alt="jobit_recruiter_listing_details" src="https://github.com/user-attachments/assets/8b0ec0d2-489a-40da-8612-b7806146fa9f" />

*Recruiter view of a job listing with candidate applications, skill tags, and AI-based matching percentage.*

---

### 💬 Messaging
<img width="1920" height="878" alt="jobit_send_message" src="https://github.com/user-attachments/assets/62633805-cb6e-46f7-9960-405591bc5473" />

*Direct communication between recruiters and candidates for interview scheduling and feedback.*

---

### 🔐 Password Reset Flow
<img width="1920" height="878" alt="jobit_reset_email_request" src="https://github.com/user-attachments/assets/2c53b90f-6b29-4594-b95d-258ceb189aac" />

*Users can request a password reset link by providing their email address.*

<img width="1897" height="875" alt="jobit_reset_email_password" src="https://github.com/user-attachments/assets/9b02bede-c9d2-4894-a2a7-148231e0a14a" />

*Email with a secure link to reset the password, valid for 24 hours.*


## 🗺️ System Architecture

The application follows a modular, scalable architecture built with Django. Each core functionality is implemented as a separate Django app to ensure maintainability and clarity.

---

## 🧩 Component Diagram

The following diagram illustrates how the internal components of the system interact:

![Components-Diagram](https://github.com/user-attachments/assets/33bf8c30-0c24-40b9-bd8f-1bea2f745baf)

*Each component is responsible for a distinct area of functionality, such as user management, job posting, or chat messaging.*

---

## 🗃️ Database Schema

This relational model outlines how the core entities relate to one another:

<img width="698" height="690" alt="database" src="https://github.com/user-attachments/assets/fb2952c1-86ca-4593-a1b5-2478fd59a3d8" />

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
