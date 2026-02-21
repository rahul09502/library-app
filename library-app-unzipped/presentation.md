Library App — Project Overview & Steps
=====================================

1. Project goal
- Build a simple Department Library web app where students can search, borrow, and return books; admins manage inventory.

2. Tech stack
- Backend: Python 3 + Flask
- Database: SQLite (file `instance/library.db`)
- Frontend: HTML, CSS, JavaScript, Bootstrap 5

3. What I implemented
- Search API (`/api/search`) with filters: department, year range, availability.
- Admin pages: login, dashboard, add/edit/delete books.
- Student flows: register, login, borrow (limit 3), return, dashboard.
- CSRF protection via Flask-WTF.
- Dockerfile and `docker-compose.yml` for containerization.

4. Development steps followed (high level)
- Scaffolded Flask app and templates.
- Designed DB schema and wrote `create_db.py` to create tables and seed sample data.
- Implemented routes in `app.py` for API and UI.
- Added client-side JavaScript for search and borrow interactions.
- Added CSS and images for UI polish.
- Wrote and ran `pytest` tests to validate core flows.
- Documented run steps and packaged the project into a ZIP.

5. Sample books seeded (from `create_db.py`)

| Title | Author | Year | ISBN | Copies | Department |
|-------|--------|------:|------|-------:|------------|
| Introduction to Algorithms | Cormen, Leiserson, Rivest | 2009 | 0262033844 | 3 | CSE |
| Clean Code | Robert C. Martin | 2008 | 0132350882 | 2 | CSE |
| Linear Algebra and Its Applications | Gilbert Strang | 2016 | 0980232776 | 1 | Math |
| Database System Concepts | Silberschatz, Korth, Sudarshan | 2010 | 0073523321 | 2 | CSE |
| Artificial Intelligence: A Modern Approach | Stuart Russell, Peter Norvig | 2010 | 0136042597 | 2 | CSE |
| Operating System Concepts | Silberschatz, Galvin, Gagne | 2018 | 1119456339 | 2 | CSE |
| Discrete Mathematics and Its Applications | Kenneth H. Rosen | 2011 | 0073383090 | 1 | Math |
| Computer Networks | Andrew S. Tanenbaum | 2010 | 0132126958 | 1 | CSE |
| Principles of Compiler Design | Aho, Ullman | 2007 | 0201003003 | 1 | CSE |
| Modern Database Management | Jeffrey A. Hoffer | 2012 | 0136086203 | 1 | CSE |

6. How to run locally (summary)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python create_db.py
python app.py
```

7. Deliverables in this folder
- `app.py`, `create_db.py`, `templates/`, `static/`, `presentation.md`

8. Notes for presentation
- Use the app demo (http://127.0.0.1:5000) to show search/borrow flows.
- Admin default password (for demo) is `rahul@123` or set `LIB_ADMIN_PASS` env var.
