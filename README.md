# SkillMatch+ Backend

**Project #38 — Helwan National University, BIDT 2025**
Backend Specialist: Victoria Marawan Nabil Gad

---

## Tech Stack

| Layer        | Technology                  |
|--------------|-----------------------------|
| Language     | Python 3.11                 |
| Framework    | Flask 3.0                   |
| Database     | MySQL 8.0 (InnoDB, utf8mb4) |
| Auth         | JWT (flask-jwt-extended)    |
| AI           | OpenAI GPT-4o-mini API      |
| Password     | bcrypt                      |
| CORS         | flask-cors                  |
| Server       | Gunicorn (production)       |

---

## Project Structure

```
skillmatch_backend/
├── app/
│   ├── __init__.py          # Application factory
│   ├── db.py                # MySQL connection pool
│   ├── models/
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── company.py
│   │   ├── assessment.py    # CareerAssessment, CareerPersona, LearningRoadmap
│   │   ├── task.py          # MicroTask, TaskSubmission, PortfolioItem
│   │   ├── internship.py    # Internship, InternshipApplication
│   │   └── notification.py
│   ├── routes/
│   │   ├── auth.py          # /api/auth/*
│   │   ├── students.py      # /api/students/*
│   │   ├── companies.py     # /api/companies/*
│   │   ├── assessment.py    # /api/assessment/*
│   │   ├── roadmap.py       # /api/roadmap/*
│   │   ├── tasks.py         # /api/tasks/*
│   │   ├── portfolio.py     # /api/portfolio/*
│   │   ├── internships.py   # /api/internships/*
│   │   ├── notifications.py # /api/notifications/*
│   │   └── admin.py         # /api/admin/*
│   ├── services/
│   │   ├── ai_service.py    # GPT-4o-mini integration
│   │   └── portfolio_service.py
│   └── utils/
│       ├── responses.py     # success() / error() helpers
│       ├── decorators.py    # @student_required, @company_required, @admin_required
│       └── validators.py    # email, password, field validators
├── tests/
│   ├── test_auth.py
│   └── test_validators.py
├── schema.sql               # Complete MySQL schema + seed data
├── run.py                   # Development entry point
├── requirements.txt
├── .env.example
└── SkillMatch_API.postman_collection.json
```

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/your-team/skillmatch-backend.git
cd skillmatch-backend
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your DB credentials and OpenAI API key
```

### 3. Create database

```bash
mysql -u root -p < schema.sql
```

### 4. Run development server

```bash
python run.py
```

Server starts at `http://localhost:5000`

### 5. Run tests

```bash
pytest tests/ -v
```

---
Base URL: http://127.0.0.1:5000

## API Reference

### Authentication
| Method | Endpoint              | Access  | Description                  |
|--------|-----------------------|---------|------------------------------|
| POST   | /api/auth/register    | Public  | Register student or company  |
| POST   | /api/auth/login       | Public  | Login and receive JWT token  |
| GET    | /api/auth/me          | Any     | Get current user info        |

### Student
| Method | Endpoint                   | Access  | Description              |
|--------|----------------------------|---------|--------------------------|
| GET    | /api/students/profile      | Student | Get own profile          |
| PUT    | /api/students/profile      | Student | Update profile           |
| GET    | /api/students/skills       | Student | Get skill list           |
| POST   | /api/students/skills       | Student | Add a skill              |
| GET    | /api/students/dashboard    | Student | Unified dashboard        |

### Assessment (AI Pipeline)
| Method | Endpoint                    | Access  | Description                     |
|--------|-----------------------------|---------|---------------------------------|
| GET    | /api/assessment/questions   | Student | Load quiz questions             |
| POST   | /api/assessment/submit      | Student | Submit quiz → trigger AI        |
| GET    | /api/assessment/persona     | Student | Get latest persona + roadmap    |
| GET    | /api/assessment/history     | Student | All past assessment sessions    |

### Roadmap
| Method | Endpoint                               | Access  | Description             |
|--------|----------------------------------------|---------|-------------------------|
| GET    | /api/roadmap/                          | Student | Get active roadmap      |
| PATCH  | /api/roadmap/courses/{id}/complete     | Student | Mark course completed   |
| PATCH  | /api/roadmap/courses/{id}/start        | Student | Mark course in progress |
| PATCH  | /api/roadmap/status                    | Student | Update roadmap status   |

### Tasks
| Method | Endpoint                              | Access          | Description               |
|--------|---------------------------------------|-----------------|---------------------------|
| GET    | /api/tasks/                           | Any auth        | List active tasks         |
| POST   | /api/tasks/                           | Company         | Create new task           |
| POST   | /api/tasks/{id}/submit                | Student         | Submit task solution      |
| GET    | /api/tasks/my-submissions             | Student         | My submission history     |
| GET    | /api/tasks/submissions/{task_id}      | Company         | View task submissions     |
| PATCH  | /api/tasks/submissions/{id}/review    | Company / Admin | Approve or reject         |

### Internships
| Method | Endpoint                                  | Access         | Description                     |
|--------|-------------------------------------------|----------------|---------------------------------|
| GET    | /api/internships/                         | Student        | List with AI match scores       |
| POST   | /api/internships/                         | Company        | Post internship                 |
| POST   | /api/internships/{id}/apply               | Student        | Apply with AI match             |
| GET    | /api/internships/my-applications          | Student        | Track my applications           |
| GET    | /api/internships/company                  | Company        | My posted internships           |
| GET    | /api/internships/{id}/applicants          | Company        | View ranked applicants          |
| PATCH  | /api/internships/applications/{id}/status | Company/Admin  | Update application status       |

### Portfolio
| Method | Endpoint                        | Access  | Description              |
|--------|---------------------------------|---------|--------------------------|
| GET    | /api/portfolio/                 | Student | Get own portfolio        |
| GET    | /api/portfolio/public/{id}      | Public  | View public portfolio    |
| PATCH  | /api/portfolio/{id}/visibility  | Student | Toggle public/private    |

### Admin
| Method | Endpoint                             | Access | Description            |
|--------|--------------------------------------|--------|------------------------|
| GET    | /api/admin/dashboard                 | Admin  | Platform metrics       |
| GET    | /api/admin/users                     | Admin  | List all users         |
| PATCH  | /api/admin/users/{id}/activate       | Admin  | Activate/deactivate    |
| PATCH  | /api/admin/users/{id}/verify-company | Admin  | Verify company         |
| GET    | /api/admin/tasks/pending-review      | Admin  | Tasks awaiting review  |
| PATCH  | /api/admin/tasks/{id}/approve        | Admin  | Approve/reject task    |
| GET    | /api/admin/submissions/pending       | Admin  | All pending reviews    |

---

## AI Integration

### How it works

1. Student submits quiz answers → `POST /api/assessment/submit`
2. Flask calls `ai_service.generate_persona(answers)` 
3. GPT-4o-mini receives a structured system prompt + the answers
4. Returns JSON: `persona_title`, `skill_gaps`, `top_career_paths`, `roadmap_steps`
5. Persona and roadmap saved to MySQL
6. On internship browsing: `ai_service.calculate_match_score()` scores each listing

### AI Response Format

```json
{
  "persona_title": "The Analytical Builder",
  "persona_description": "...",
  "top_career_paths": ["Backend Developer", "Data Engineer", "System Analyst"],
  "strengths": ["Systematic thinking", "Problem solving", "Detail orientation", "Research"],
  "skill_gaps": ["Machine Learning", "Cloud Deployment", "Docker", "System Design"],
  "roadmap_steps": [
    { "step": 1, "title": "Foundation", "description": "...", "courses": ["Python for Everybody"] },
    { "step": 2, "title": "Core Skills", "description": "...", "courses": ["Flask Mega-Tutorial", "MySQL for Developers"] },
    { "step": 3, "title": "Specialisation", "description": "...", "courses": ["Machine Learning Specialization"] }
  ]
}
```

---

## Production Deployment

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

Set `FLASK_ENV=production` in `.env` for production mode.

---

*SkillMatch+ — Bridging the gap between students and employers through AI.*
