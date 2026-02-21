Library App — Local Run Instructions

Environment
- The application reads the admin password from the environment variable `LIB_ADMIN_PASS`.
- For convenience the default admin password is set to `rahul@123`. For production, set a secure password in the environment.

Run locally (Windows PowerShell):

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. (Optional) Set admin password via env var:

```powershell
$env:LIB_ADMIN_PASS = 'rahul@123'
```

4. Create the database and seed sample data:

```powershell
python create_db.py
```

5. Run the app:

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

Security note: Do not commit real secrets. Use environment variables in production.
# Department Library App (Minimal)

Simple Flask + SQLite app for browsing/searching department library books.

Quick start

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

2. Install deps and create the database:

```bash
pip install -r requirements.txt
python create_db.py
```

3. Run the app:

```bash
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

Docker
------
Build and run with Docker (recommended for deployment):

From the `git/library_app` folder build the image and start:

```bash
docker compose up --build
```

This binds host port 5000 to the container. The SQLite database is persisted in `./instance` (a local folder created automatically).

Environment variables
- `LIB_APP_SECRET` — Flask secret key (set to a secure value in production)
- `LIB_ADMIN_PASS` — Admin password

Deploy notes
- The image runs with `gunicorn app:app` (see `Dockerfile`).
- For production, set secure env vars and consider using a more robust DB (Postgres) if concurrent writes or scaling is required.

Publish to Docker Hub
---------------------
Option A — manual (local):

1. Build the image locally and tag it with your Docker Hub username:

```bash
docker build -t <your-dockerhub-username>/library-app:latest .
```

2. Login and push:

```bash
docker login
docker push <your-dockerhub-username>/library-app:latest
```

Option B — automated via GitHub Actions:

1. Create two repository secrets in GitHub: `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` (a Docker Hub access token or password).
2. Push to the `main` branch; the workflow `.github/workflows/docker-publish.yml` will build and push `DOCKERHUB_USERNAME/library-app:latest`.

After publishing
- Pull and run on any host:

```bash
docker run -p 5000:5000 -v ./instance:/app/instance -e LIB_APP_SECRET=change-me -e LIB_ADMIN_PASS=admin123 <your-dockerhub-username>/library-app:latest
```

Testing
-------
Run the unit tests locally with `pytest` from the `git/library_app` folder:

```bash
venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

The tests create the sample database (if missing) and run basic API and auth flows. CSRF is disabled during tests via app config.


