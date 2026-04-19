-- ============================================================
--  SkillMatch+ Database Schema
--  Engine: InnoDB | Charset: utf8mb4 | Version: 1.0
--  Project #38 — Helwan National University BIDT 2025
-- ============================================================

CREATE DATABASE IF NOT EXISTS skillmatch_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE skillmatch_db;

-- ── USERS ────────────────────────────────────────────────────
CREATE TABLE users (
  id            INT          AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(120) NOT NULL,
  email         VARCHAR(180) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('student','company','admin') NOT NULL DEFAULT 'student',
  phone         VARCHAR(20),
  is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_email (email),
  INDEX idx_role  (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── STUDENT PROFILES ────────────────────────────────────────
CREATE TABLE student_profiles (
  id              INT          AUTO_INCREMENT PRIMARY KEY,
  user_id         INT          NOT NULL UNIQUE,
  university      VARCHAR(200),
  major           VARCHAR(200),
  graduation_year YEAR,
  linkedin_url    VARCHAR(300),
  github_url      VARCHAR(300),
  avatar_url      VARCHAR(300),
  created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── COMPANY PROFILES ────────────────────────────────────────
CREATE TABLE company_profiles (
  id           INT          AUTO_INCREMENT PRIMARY KEY,
  user_id      INT          NOT NULL UNIQUE,
  company_name VARCHAR(200) NOT NULL,
  industry     VARCHAR(100),
  website      VARCHAR(300),
  description  TEXT,
  logo_url     VARCHAR(300),
  is_verified  BOOLEAN      NOT NULL DEFAULT FALSE,
  created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── CAREER ASSESSMENTS ──────────────────────────────────────
CREATE TABLE career_assessments (
  id              INT       AUTO_INCREMENT PRIMARY KEY,
  student_id      INT       NOT NULL,
  quiz_responses  JSON      NOT NULL,
  ai_raw_response JSON,
  taken_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
  INDEX idx_student_assess (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── CAREER PERSONAS ─────────────────────────────────────────
CREATE TABLE career_personas (
  id                  INT          AUTO_INCREMENT PRIMARY KEY,
  assessment_id       INT          NOT NULL UNIQUE,
  student_id          INT          NOT NULL,
  persona_title       VARCHAR(200) NOT NULL,
  persona_description TEXT,
  top_career_paths    JSON,
  strengths           JSON,
  skill_gaps          JSON,
  generated_at        TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (assessment_id) REFERENCES career_assessments(id) ON DELETE CASCADE,
  FOREIGN KEY (student_id)    REFERENCES student_profiles(id)   ON DELETE CASCADE,
  INDEX idx_student_persona (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── LEARNING ROADMAPS ───────────────────────────────────────
CREATE TABLE learning_roadmaps (
  id            INT          AUTO_INCREMENT PRIMARY KEY,
  student_id    INT          NOT NULL,
  persona_id    INT          NOT NULL,
  career_path   VARCHAR(200),
  roadmap_steps JSON,
  status        ENUM('active','completed','paused') DEFAULT 'active',
  created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
  FOREIGN KEY (persona_id) REFERENCES career_personas(id)  ON DELETE CASCADE,
  INDEX idx_student_roadmap (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── COURSES ─────────────────────────────────────────────────
CREATE TABLE courses (
  id               INT          AUTO_INCREMENT PRIMARY KEY,
  title            VARCHAR(300) NOT NULL,
  provider         VARCHAR(100),
  url              VARCHAR(500),
  category         VARCHAR(100),
  difficulty_level ENUM('beginner','intermediate','advanced') DEFAULT 'beginner',
  duration_hours   INT,
  is_active        BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── ROADMAP COURSES (junction) ──────────────────────────────
CREATE TABLE roadmap_courses (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  roadmap_id   INT NOT NULL,
  course_id    INT NOT NULL,
  order_index  INT NOT NULL DEFAULT 0,
  status       ENUM('pending','in_progress','completed') DEFAULT 'pending',
  completed_at TIMESTAMP NULL,
  FOREIGN KEY (roadmap_id) REFERENCES learning_roadmaps(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id)  REFERENCES courses(id)           ON DELETE CASCADE,
  UNIQUE KEY uq_roadmap_course (roadmap_id, course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── SKILLS ──────────────────────────────────────────────────
CREATE TABLE skills (
  id       INT          AUTO_INCREMENT PRIMARY KEY,
  name     VARCHAR(100) NOT NULL UNIQUE,
  category VARCHAR(100),
  level    ENUM('beginner','intermediate','advanced')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── STUDENT SKILLS (junction) ───────────────────────────────
CREATE TABLE student_skills (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  student_id  INT NOT NULL,
  skill_id    INT NOT NULL,
  proficiency ENUM('beginner','intermediate','advanced') DEFAULT 'beginner',
  is_verified BOOLEAN DEFAULT FALSE,
  acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
  FOREIGN KEY (skill_id)   REFERENCES skills(id)           ON DELETE CASCADE,
  UNIQUE KEY uq_student_skill (student_id, skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── MICRO TASKS ─────────────────────────────────────────────
CREATE TABLE micro_tasks (
  id          INT          AUTO_INCREMENT PRIMARY KEY,
  company_id  INT          NOT NULL,
  title       VARCHAR(300) NOT NULL,
  description TEXT,
  category    VARCHAR(100),
  difficulty  ENUM('easy','medium','hard') DEFAULT 'medium',
  points      INT DEFAULT 10,
  is_active   BOOLEAN DEFAULT TRUE,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (company_id) REFERENCES company_profiles(id) ON DELETE CASCADE,
  INDEX idx_company_tasks (company_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── TASK SUBMISSIONS ────────────────────────────────────────
CREATE TABLE task_submissions (
  id                 INT AUTO_INCREMENT PRIMARY KEY,
  student_id         INT NOT NULL,
  task_id            INT NOT NULL,
  submission_content TEXT,
  submission_url     VARCHAR(500),
  status             ENUM('pending','approved','rejected') DEFAULT 'pending',
  score              INT DEFAULT 0,
  feedback           TEXT,
  submitted_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  reviewed_at        TIMESTAMP NULL,
  FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
  FOREIGN KEY (task_id)    REFERENCES micro_tasks(id)      ON DELETE CASCADE,
  INDEX idx_student_sub (student_id),
  INDEX idx_task_sub    (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── PORTFOLIO ITEMS ─────────────────────────────────────────
CREATE TABLE portfolio_items (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  student_id    INT NOT NULL,
  submission_id INT NOT NULL,
  title         VARCHAR(300),
  description   TEXT,
  item_url      VARCHAR(500),
  is_public     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id)    REFERENCES student_profiles(id) ON DELETE CASCADE,
  FOREIGN KEY (submission_id) REFERENCES task_submissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── INTERNSHIPS ─────────────────────────────────────────────
CREATE TABLE internships (
  id                   INT          AUTO_INCREMENT PRIMARY KEY,
  company_id           INT          NOT NULL,
  title                VARCHAR(300) NOT NULL,
  description          TEXT,
  location             VARCHAR(200),
  is_remote            BOOLEAN DEFAULT FALSE,
  required_skills      JSON,
  duration_weeks       INT,
  status               ENUM('active','closed','draft') DEFAULT 'active',
  application_deadline DATE,
  created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (company_id) REFERENCES company_profiles(id) ON DELETE CASCADE,
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── INTERNSHIP APPLICATIONS ─────────────────────────────────
CREATE TABLE internship_applications (
  id              INT   AUTO_INCREMENT PRIMARY KEY,
  student_id      INT   NOT NULL,
  internship_id   INT   NOT NULL,
  ai_match_score  FLOAT DEFAULT 0.0,
  match_breakdown JSON,
  cover_note      TEXT,
  status          ENUM('pending','reviewed','accepted','rejected') DEFAULT 'pending',
  applied_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id)    REFERENCES student_profiles(id) ON DELETE CASCADE,
  FOREIGN KEY (internship_id) REFERENCES internships(id)      ON DELETE CASCADE,
  UNIQUE KEY uq_application   (student_id, internship_id),
  INDEX idx_match_score       (ai_match_score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── NOTIFICATIONS ───────────────────────────────────────────
CREATE TABLE notifications (
  id         INT          AUTO_INCREMENT PRIMARY KEY,
  user_id    INT          NOT NULL,
  title      VARCHAR(200) NOT NULL,
  message    TEXT,
  type       ENUM('info','success','warning','error') DEFAULT 'info',
  is_read    BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_unread (user_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── SEED: SKILLS CATALOG ────────────────────────────────────
INSERT INTO skills (name, category, level) VALUES
('Python',          'Programming',   'intermediate'),
('Flask',           'Backend',       'intermediate'),
('MySQL',           'Database',      'beginner'),
('REST API Design', 'Backend',       'intermediate'),
('JavaScript',      'Programming',   'beginner'),
('React.js',        'Frontend',      'intermediate'),
('Git',             'DevOps',        'beginner'),
('SQL',             'Database',      'beginner'),
('Data Analysis',   'Data',         'beginner'),
('Machine Learning','AI/ML',         'advanced'),
('Communication',   'Soft Skills',   'beginner'),
('Project Management','Soft Skills', 'intermediate');

-- ── SEED: COURSES CATALOG ───────────────────────────────────
INSERT INTO courses (title, provider, url, category, difficulty_level, duration_hours) VALUES
('Python for Everybody',           'Coursera',  'https://coursera.org/learn/python',          'Programming', 'beginner',     30),
('The Flask Mega-Tutorial',        'Miguel',    'https://blog.miguelgrinberg.com/flask',       'Backend',     'intermediate', 20),
('MySQL for Developers',           'PlanetScale','https://planetscale.com/learn/mysql',        'Database',    'beginner',     15),
('REST API Design Fundamentals',   'Udemy',     'https://udemy.com/rest-api',                 'Backend',     'intermediate', 10),
('React — The Complete Guide',     'Udemy',     'https://udemy.com/react-complete-guide',     'Frontend',    'intermediate', 48),
('Git and GitHub for Beginners',   'freeCodeCamp','https://freecodecamp.org/git',             'DevOps',      'beginner',      5),
('SQL Bootcamp',                   'Udemy',     'https://udemy.com/sql-bootcamp',             'Database',    'beginner',     14),
('Machine Learning Specialization','Coursera',  'https://coursera.org/specializations/ml',   'AI/ML',       'advanced',     90);
