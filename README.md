# Team Task Manager

Team Task Manager is a production-ready Django task collaboration platform for small teams and internal operations groups. Admins can create projects, manage team members, assign and monitor tasks, and track delivery metrics. Members get a focused workspace for reviewing their assigned work, updating status, and keeping deadlines visible.

## Features

- Role-based authentication with `Admin` and `Member` access levels
- Session-based login for templates plus JWT authentication for REST APIs
- Custom user model with profile details and role handling
- Project management with team assignment and progress tracking
- Task management with status, priority, due dates, and overdue highlighting
- Admin dashboard with analytics, progress bars, charts, and recent activity
- Member dashboard with personal workload stats and deadline views
- Search, filtering, pagination, modal forms, validation, and toast notifications
- Activity logging for project/task creation, updates, status changes, and deletion
- Railway deployment support with PostgreSQL, Gunicorn, WhiteNoise, and `.env`

## Tech Stack

- Backend: Django, Django REST Framework, Simple JWT
- Database: PostgreSQL
- Frontend: Bootstrap 5, HTML, CSS, JavaScript, Chart.js
- Deployment: Railway, Gunicorn, WhiteNoise

## Folder Structure

```text
Team Task Manager/
├── accounts/
├── api/
├── core/
├── dashboard/
├── projects/
├── tasks/
├── static/
├── templates/
├── manage.py
├── requirements.txt
├── Procfile
├── runtime.txt
└── .env.example
```

## Core Roles

### Admin

- Create, edit, and delete projects
- Manage team membership for each project
- Create, edit, assign, and delete tasks
- View organization-wide analytics and activity

### Member

- View assigned tasks
- Update task status
- Access a personal dashboard with workload visibility

## Data Model Overview

- `accounts.User`
  - Extends `AbstractUser`
  - Stores `role`, `bio`, `email`
- `projects.Project`
  - `created_by` -> `User`
  - `team_members` <-> `User`
- `tasks.Task`
  - `project` -> `Project`
  - `assigned_to` -> `User`
  - `created_by` -> `User`
- `dashboard.ActivityLog`
  - Stores recent activity for dashboards

## Installation

### 1. Clone and enter the project

```bash
git clone <your-repository-url>
cd "Team Task Manager"
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Update `.env` with your PostgreSQL connection values.

### 5. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Environment Notes

- `DATABASE_URL` is the preferred production database setting.
- If `DATABASE_URL` is not provided, the app can also read explicit PostgreSQL variables.
- A SQLite fallback is present for quick local bootstrapping when PostgreSQL is not available.
- `ALLOW_ADMIN_SIGNUP=True` is convenient for demos. Set it to `False` in production if admins should only be created by existing admins or the Django admin panel.
- For HTTPS deployments, set `SECURE_SSL_REDIRECT=True`, `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`, and `SECURE_HSTS_PRELOAD=True` after your domain is stable.

## REST API

### Authentication

- `POST /api/signup/`
- `POST /api/login/`
- `POST /api/logout/`

Sample signup payload:

```json
{
  "username": "adminuser",
  "email": "admin@example.com",
  "first_name": "Asha",
  "last_name": "Sharma",
  "role": "ADMIN",
  "bio": "Operations lead",
  "password": "StrongPass123",
  "password_confirm": "StrongPass123"
}
```

### Projects

- `GET /api/projects/`
- `POST /api/projects/create/`
- `PUT /api/projects/<id>/update/`
- `DELETE /api/projects/<id>/delete/`

Sample project create payload:

```json
{
  "name": "Q3 Launch",
  "description": "Cross-functional release planning",
  "team_member_ids": [2, 3, 4]
}
```

### Tasks

- `GET /api/tasks/`
- `POST /api/tasks/create/`
- `PUT /api/tasks/<id>/update/`
- `DELETE /api/tasks/<id>/delete/`

Sample task create payload:

```json
{
  "title": "Prepare launch checklist",
  "description": "Create the final go-live checklist",
  "project_id": 1,
  "assigned_to_id": 3,
  "status": "TODO",
  "priority": "HIGH",
  "due_date": "2026-05-30"
}
```

Members can only update the `status` field through the update endpoint.

### Dashboard

- `GET /api/dashboard/`

Returns role-aware dashboard statistics and activity data.

## Railway Deployment

### 1. Create a new Railway project

- Add a PostgreSQL service
- Add the GitHub repository or deploy from local source

### 2. Configure Railway environment variables

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=.up.railway.app`
- `CSRF_TRUSTED_ORIGINS=https://<your-app>.up.railway.app`
- `DATABASE_URL` from the Railway PostgreSQL plugin
- `ALLOW_ADMIN_SIGNUP=False` for production if preferred
- `SECURE_SSL_REDIRECT=True`
- `SECURE_HSTS_SECONDS=31536000`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
- `SECURE_HSTS_PRELOAD=True`

### 3. Ensure build/runtime files are present

- `requirements.txt`
- `Procfile`
- `runtime.txt`

### 4. Deploy

Railway will install dependencies, run the `web` process from the `Procfile`, and serve static files through WhiteNoise.

### 5. Run migrations

Use the Railway shell or a post-deploy command:

```bash
python manage.py migrate
python manage.py createsuperuser
```

## UI Pages Included

- Login page
- Signup page
- Admin dashboard
- Member dashboard
- Project management page
- Task management page
- Team management page
- Profile page

## Security Notes

- Django password hashing
- CSRF middleware enabled
- Role-based view restrictions for both templates and APIs
- JWT validation via Simple JWT
- Session authentication for server-rendered pages
- Unauthorized access redirected or blocked with proper API permissions


## Future Improvements

- Refresh-token rotation endpoint
- Email notifications for overdue tasks
- Drag-and-drop board view
- Audit exports and CSV reporting

## License

Use this project for learning, demos, or internal tooling customization.


## Deployment Link

https://web-production-3f4a6.up.railway.app/
