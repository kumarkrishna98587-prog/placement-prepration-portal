# Placement Preparation Portal

A beginner-friendly diploma final-year Flask web application.

## Features
- Student registration and login
- Student dashboard
- Aptitude MCQ quiz with automatic score
- Quiz score history
- Interview preparation questions
- Simple resume preview form
- SQLite database

## Run locally
1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. In terminal run:
   ```bash
   python -m venv .venv
   ```
4. Activate:
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`
   - Windows CMD: `.venv\Scripts\activate.bat`
5. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
6. Start:
   ```bash
   python app.py
   ```
7. Open `http://127.0.0.1:5000`

## Important deployment note
The included Render configuration is a demo deployment starter. Render free web services have an ephemeral local filesystem, so SQLite changes can be lost after restarts/redeploys. For durable online student accounts and scores, configure a persistent external database before using it beyond a classroom demo. Never put real student personal data into a public demo.

Change `SECRET_KEY` to a long random value in your hosting provider's environment settings. Free hosting may sleep while idle and may have other limits.
