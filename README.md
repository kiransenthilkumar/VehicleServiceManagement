# Vehicle Service Management Website

> Simple Flask-based vehicle service management system (for development/testing).

## Prerequisites
- Python 3.9+ installed
- Git (optional)

## Setup (Windows - PowerShell)

1. Create and activate virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Initialize and seed the database

```powershell
# This script resets and seeds the DB with sample users, vehicles, services, and invoices
python seed_data.py
```

4. Run the application

```powershell
python run.py
# By default the app runs on http://127.0.0.1:5000
```

## Uploading sample images
Place vehicle image files (if used) into `static/uploads/`. The seed script prints expected filenames.

## Default user login details

Use these accounts to log in during development or testing.

| Role     | Username | Email                     | Password    | Notes |
|----------|----------|---------------------------|-------------|-------|
| Admin    | admin    | admin@vehiclecare.local   | admin123    | Full admin access |
| Customer | sundar   | sundar@example.com        | password123 | Seeded customer |
| Customer | meena    | meena@example.com         | password123 | Seeded customer |
| Customer | arun     | arun@example.com          | password123 | Seeded customer |
| Customer | lakshmi  | lakshmi@example.com       | password123 | Seeded customer |
| Customer | karthik  | karthik@example.com       | password123 | Seeded customer |
| Customer | sachin   | sachin@example.com        | password123 | Seeded customer |
| Customer | nishanth | nishanth@example.com      | password123 | Seeded customer |
| Customer | mouli    | mouli@example.com         | password123 | Seeded customer |

Notes:
- The `seed_data.py` script resets the database and creates these users and sample records.
- If you change credentials in seed data, update this README accordingly.

## Helpful tips
- To run in a different environment (WSL/CMD/macOS), use the appropriate virtualenv activation command.
- Add vehicle images into `static/uploads/` to avoid broken image placeholders.

## Where to look in the project
- Application entry: `run.py`
- Flask app factory and models: `app/__init__.py`, `app/models.py`
- Seed script: `seed_data.py`

---
Generated on: February 28, 2026
