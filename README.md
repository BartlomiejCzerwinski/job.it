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

![database](https://github.com/user-attachments/assets/d172af03-ad89-434a-9807-473caad89b6f)

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

To run the application locally:

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/job.it.git
   cd job.it
