# job.it

**job.it** is a modular web application designed to support and streamline the recruitment process in the IT industry. The platform brings together job seekers and employers, providing tools for job searching, applications, communication, and intelligent job matching.

---

## 🗺️ System Architecture

![Applications-Diagram](https://github.com/user-attachments/assets/6fba49a9-da47-4db6-9fb0-f52ea53d2b30)

*Note: The diagram above presents a high-level overview of the system's architecture.*

---

## 🧩 Main Modules

### Users
Handles user registration, authentication, session management, and user profile operations.

### Messaging (Chat)
Enables direct communication between users, including messaging and contact management.

### Applications
Manages the process of submitting, tracking, and managing job applications.

### Jobs
Responsible for creating, listing, and managing job offers posted by employers.

### Matching
Implements job recommendation and prediction models to match users with relevant job offers based on their profiles and activity.

![Components-Diagram](https://github.com/user-attachments/assets/33bf8c30-0c24-40b9-bd8f-1bea2f745baf)


---

## 🚀 Getting Started

1. **Clone the repository**
2. **Install dependencies** for each module (see individual module folders for requirements)
3. **Run the Django server** using `python manage.py runserver`
4. Access the application via your browser at `http://localhost:8000/`

---

## 🛠️ Technologies Used

- Python & Django (backend)
- SQLite (default database, can be replaced)
- HTML/CSS (frontend templates)
