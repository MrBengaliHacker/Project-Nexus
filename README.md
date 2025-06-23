# Our Mission

Redesign the existing website of Bengal Institute of Technology into a fully-featured, modern web platform that not only elevates the digital experience of students and faculty but also showcases our development capabilities as a part of the Tech Fest 2025 at BIT.

The project aims to build a centralized digital ecosystem that addresses real academic and administrative pain points. This platform will integrate seamless result access, curated academic resources, real-time announcements, AI-powered assistance, and social interaction tools — all within a responsive, mobile-optimized web portal designed for the BIT community.

---

# Problems We’re Solving

| Problem | Current Situation | Our Proposed Solution |
| --- | --- | --- |
| Result access is inconvenient | The official MAKAUT result portal is slow, unreliable on mobile, and lacks clarity | Built-in result viewing with a clean, intuitive UI and an integrated SGPA/CGPA calculator |
| Study materials are disorganized | Notes and syllabus are scattered across various platforms (WhatsApp, Google Drive, etc.) | Centralized resource hub with subject-wise folders, downloadable content, and search functionality |
| Missed announcements/events | No formal communication system for students; updates are shared irregularly | Official announcement board where class representatives and faculty can post updates and event info |
| No immediate support channel | Students depend on CRs, seniors, or manually searching for information | AI-powered chatbot that answers college-related FAQs, available 24/7 |
| Outdated website | The current site is static, lacks responsiveness, and offers limited interactivity | A modern, interactive, and feature-rich web portal optimized for both desktop and mobile devices |
| Lack of student interaction | No common digital space for students to express opinions or ask questions | Campus feed for posts, discussions, polls, and Q&A with support for likes and comments |
| Timetable tracking is manual | Students manually check schedules; no reminders or updates | Smart timetable with automatic class reminders, schedule updates, and calendar integration |
| Unsafe feedback system | Students hesitate to report issues or suggest improvements | Anonymous feedback and complaint form to ensure privacy and honesty |

---

### Selected Tech Stack

| Component | Technology Options |
| --- | --- |
| Frontend | HTML, CSS, JavaScript with Tailwind CSS and DaisyUI V5 (or alternative component libraries) |
| Backend  | Django (preferred for scalability and admin capabilities) / Flask (lightweight alternative) |
| Database | PostgreSQL (primary), SQLite (only for development/small-scale demo), MongoDB (alternative, though not preferred) |
| File Storage | Supabase (up to 5 GB), Cloudinary (up to 10 GB), Synology NAS (up to 15 GB) — subject to final evaluation |
| Others | Socket.io (for live chat, comments, event updates, and feed interaction) |

---

### Key Features To Implement

- [ ]  **Seamless Result Checking**
    
    Easily accessible result section with semester-wise breakdown and auto-calculated CGPA/SGPA
    
- [ ]  **Organized Notes and Syllabus Access**
    
    Structured repository of academic materials, available by semester and subject with search filters
    
- [ ]  **Centralized Announcement Board**
    
    Official space for CRs and faculty to post notices, events, and deadline alerts in real time
    
- [ ]  **Event Listings and Participation Info**
    
    Calendar and detailed event cards showing ongoing/upcoming events, rules, and registration links
    
- [ ]  **AI Chatbot Assistant**
    
    Smart virtual assistant that can answer FAQs about academics, campus facilities, clubs, and more
    
- [ ]  **Role-Based Dashboards**
    
    Customized dashboards for students and faculty including performance insights, shared files, announcements, etc.
    
- [ ]  **Campus Feed / Community Forum**
    
    A social space for students to ask academic or general queries, share updates, and interact freely
    
- [ ]  **Attendance Monitoring System**
    
    Track class attendance with integration for student and faculty views and potential alert features
    
- [ ]  **Feedback and Complaint System**
    
    Secure, anonymous form submission to encourage open feedback and problem reporting without fear
    
- [ ]  **PWA (Progressive Web App) Support**
    
    Allows users to install the web portal as an app on their mobile or desktop devices for quick access
    

---

## Proposed Roadmap

### Phase 1: Planning & Setup

- [ ]  Define core features (Result view, Notes, Announcements, Chatbot, Feed, etc.)
- [ ]  Gather sample data (sample results, notes, event list, etc.)
- [ ]  Finalize tech stack:
    - Flask (Backend)
    - Jinja2 (Templating)
    - Tailwind CSS + DaisyUI (Frontend)
    - PostgreSQL (Primary Database)
    - Supabase/Cloudinary for file hosting
    - Socket.io (with Flask-SocketIO)
- [ ]  Setup GitHub repo & project board (e.g., Kanban for tracking tasks)
- [ ]  Set up virtual environment + basic Flask project structure

---

### Phase 2: Backend Architecture & Auth

- [ ]  Define database schema:
    - Users (Students, Faculty)
    - Results
    - Notes
    - Announcements
    - Events
    - Feedback
    - Posts/Comments (Forum)
- [ ]  Setup Flask-Login (User authentication & session management)
- [ ]  Create role-based access (admin, faculty, student)
- [ ]  API endpoints for login, logout, and user data fetch
- [ ]  Create reusable Flask Blueprints for modular structure:
    - `auth/` - Login, registration
    - `dashboard/` - Homepage logic
    - `results/` - Result display logic
    - `resources/` - Notes, syllabus
    - `feed/` - Forum, posts, comments
    - `admin/` - Announcements, uploads

---

### Phase 3: Core Feature Development

### 1. **Result Checker**

- [ ]  Create result input form
- [ ]  Display results (with semester-wise breakdown)
- [ ]  Implement SGPA/CGPA calculator
- [ ]  (Optional) Auto-fetch from MAKAUT if possible

### 2. **Notes & Syllabus Manager**

- [ ]  Upload form for admins/faculty
- [ ]  Subject-wise file storage with categories
- [ ]  Search and filter options
- [ ]  Supabase/Cloudinary integration for file storage

### 3. **Announcements & Events**

- [ ]  Admin/CR dashboard to post announcements
- [ ]  Notification system (optional)
- [ ]  Calendar-based view for upcoming events
- [ ]  Registration or RSVP options

### 4. **Forum (Campus Feed)**

- [ ]  Post creation with tags/categories
- [ ]  Like, comment functionality
- [ ]  Real-time updates via Flask-SocketIO

### 5. **AI Chatbot (Basic Version)**

- [ ]  Train simple rule-based Q&A bot (e.g., FAQs about campus)
- [ ]  Integrate with chatbot UI (custom or prebuilt)
- [ ]  Optionally connect to OpenAI/GPT for smart answers

---

### Phase 4: Testing, Dashboard, and Polish

- [ ]  Build student & faculty dashboards (access to relevant modules only)
- [ ]  Optimize frontend with Tailwind + DaisyUI
- [ ]  Add loading spinners, alerts, form validations
- [ ]  Unit testing with `pytest`
- [ ]  Browser/device testing (mobile responsiveness)
- [ ]  Prepare demo data for presentation

---

### Phase 5: Deployment & Extras

- [ ]  Deploy using Render/Heroku/Fly.io (for quick demo) or self-hosted VPS
- [ ]  Setup environment variables securely
- [ ]  Enable HTTPS (if possible)
- [ ]  Create `.env` and configuration for production
- [ ]  Add Progressive Web App (PWA) support for mobile install:
    - `manifest.json`
    - Service Worker
- [ ]  Add anonymous feedback/complaint form (submitted to database or email)

---

### Optional Stretch Goals (Post MVP)

- [ ]  Live class timetable with reminders via email/SMS
- [ ]  OCR-based result uploading from screenshots
- [ ]  Advanced AI chatbot with dynamic knowledge base
- [ ]  Integration with college LDAP (if exists)
- [ ]  Mobile app (Flutter/PWA wrapper)

---
