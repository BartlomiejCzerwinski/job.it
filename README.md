# 💼 job.it – Intelligent Recruitment Platform for IT

**job.it** is a modular web application designed to support and streamline the recruitment process in the IT industry. The platform connects job seekers and employers, offering tools for job searching, applications, communication, and intelligent job matching based on user profiles.

---

## 🗺️ System Architecture Overview

**job.it** is a modular web application built with **Django**. Each core capability (Users, Jobs, Applications, Chat, Matching) lives in a separate Django app to keep the codebase maintainable and scalable.

**Stack**

* **Backend:** Python / Django (ORM, auth, views)
* **Frontend:** HTML, Bootstrap, JavaScript
* **Database:** SQLite for local development, PostgreSQL on production
* **AI / Recommendations:** k‑NN based matching + AI Assistant (LLM function-calling to backend services)

---

## 🧩 Component Diagram

High‑level modules and their relationships:

![Component Diagram](https://github.com/user-attachments/assets/33bf8c30-0c24-40b9-bd8f-1bea2f745baf)

**Components**

* **Users** – registration, login, profiles (skills, projects, social links), authorization.
* **Jobs** – job posting management.
* **Applications** – candidate applications and statuses.
* **Chat** – recruiter–candidate conversations and messages.
* **Matching** – recommendation engine.

---

## 🗃️ Database Schema

Relational model for users, roles, jobs, skills, applications, and chat:

<img width="698" height="690" alt="database" src="https://github.com/user-attachments/assets/fb2952c1-86ca-4593-a1b5-2478fd59a3d8" />

**Key entities:** `User`, `Location`, `Skill`, `UserSkill`, `JobListing`, `JobListingSkill`, `Project`, `SocialLink`, `ChatConversation`, `Message`, `Application`.

---

## 🔁 Sequence Diagrams

### 1) AI Recommendations

<img width="1102" height="632" alt="ai_recommendations(1)" src="https://github.com/user-attachments/assets/d383121f-9925-4408-88f0-cc9573bf3c87" />


**Flow:** UI calls `/ai/recommendations` → backend prepares context → **LLM** performs **function call** to `Recommendation Service` → DB query → job list → response rendered to UI.

### 2) Password Reset

<img width="736" height="962" alt="password_reset" src="https://github.com/user-attachments/assets/9c47904d-90f1-4365-9495-748641ae7c72" />


**Steps:** request with email → token generation + email → link validation → set new password → confirmation.

### 3) Conversation Init

<img width="952" height="612" alt="init_conversation" src="https://github.com/user-attachments/assets/4ad4a53d-a96c-4e6b-83ec-8620ed86976e" />


**Scenario:** recruiter clicks "Start conversation" → POST `/init-conversation` → check existing thread → create or reuse conversation → notify UI.

---

## 🚀 Getting Started (Docker)

### 1) Install Docker

* **Windows/Mac:** Docker Desktop
* **Linux:** Docker Engine

### 2) Clone & Run

```bash
# Clone the repository
git clone https://github.com/BartlomiejCzerwinski/job.it.git
cd job.it

# switch to a local setup branch
# git checkout local-setup

# Start the application
docker-compose up --build
```

### 3) Access the App

* **Main Application:** [http://localhost:8000](http://localhost:8000)

---

## 🎯 Works Out of the Box


- ✅ **Complete Job Board:** registration, job posting, applications
- ✅ **User Management:** login, profiles, authentication
- ✅ **File Uploads:** local storage (no cloud required)
- ✅ **Database:** SQLite with sample data
- ✅ **No API Keys Required:** everything runs locally

---

## 📸 Preview (UI Screens)

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

*Recruiter view of a job listing with candidate applications, skill tags, and AI‑based matching percentage.*

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


