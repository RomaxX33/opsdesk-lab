# OpsDesk Lab

A containerized IT operations and incident management application built as a practical portfolio project.

## Project goal

OpsDesk Lab is a hands-on project focused on IT operations, API development, database management, containerization, and DevOps practices.

The application currently provides a FastAPI service connected to PostgreSQL through Docker Compose, with health and database readiness checks.

## Technology stack

- Python
- FastAPI
- PostgreSQL 17
- Docker
- Docker Compose
- Git

## Architecture

The project uses two services managed by Docker Compose:

1. **Application (`app`):** FastAPI application served by Uvicorn.
2. **Database (`db`):** PostgreSQL database for application data.

PostgreSQL stores its data in a named Docker volume, allowing data to persist when the database container is recreated.

The application is published on `127.0.0.1:8000` by default. The database is not published on a host port.

## Repository structure

```text
app/
  __init__.py
  main.py
docs/
  architecture.md
.env
.env.example
.gitignore
compose.yaml
Dockerfile
README.md
requirements.txt
```

The local `.env` file contains environment-specific configuration and must not be committed to Git. The `.env.example` file documents the required configuration variables.

## Requirements

- Docker Desktop or Docker Engine with the Docker Compose plugin.
- Git, if cloning the repository.

Verify that Docker is running:

```bash
docker --version
docker compose version
```

## Configuration

Create a local `.env` file from the example before starting the application for the first time.

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Linux or macOS:**

```bash
cp .env.example .env
```

Edit `.env` and configure these variables:

| Variable | Purpose |
|---|---|
| `APP_PORT` | Host port for the application; defaults to `8000` if unset. |
| `POSTGRES_DB` | PostgreSQL database name. |
| `POSTGRES_USER` | PostgreSQL application database user. |
| `POSTGRES_PASSWORD` | Password for the PostgreSQL user. |

Use appropriate local credentials. Never commit `.env`, publish passwords, or include real credentials in documentation or example configuration files.

## Start the application

From the repository root, run:

```bash
docker compose up -d --build
```

This builds the application image if needed and starts the application and database in the background.

Check the service status:

```bash
docker compose ps
```

Wait until both services report a healthy status before running the checks below.

## Verify the application

### Application root

Open:

http://localhost:8000/

Expected response:

```json
{
  "application": "OpsDesk Lab",
  "version": "0.1.0",
  "status": "running"
}
```

### Application health check

Open:

http://localhost:8000/health

Expected response:

```json
{
  "status": "ok"
}
```

This endpoint checks whether the application is responding.

### Database readiness check

Open:

http://localhost:8000/ready

A successful response indicates that the application connected to PostgreSQL and executed a database query.

Expected response:

```json
{
  "status": "ready",
  "database": "connected",
  "check": 1
}
```

### API documentation

Open:

http://localhost:8000/docs

FastAPI provides interactive API documentation through Swagger UI.

## Logs and troubleshooting

Follow logs from both services:

```bash
docker compose logs -f
```

Show logs for only the application:

```bash
docker compose logs -f app
```

Show logs for only PostgreSQL:

```bash
docker compose logs -f db
```

Check PostgreSQL readiness from inside its container:

```bash
docker compose exec db pg_isready
```

List the Compose services:

```bash
docker compose config --services
```

If a service fails to start, inspect its logs and verify that `.env` contains the required variables. After correcting configuration or application code, rebuild and restart with:

```bash
docker compose up -d --build
```

## Stop the application

Stop and remove the project containers and network:

```bash
docker compose down
```

This command **preserves the named PostgreSQL data volume**.

To start the application again, run:

```bash
docker compose up -d
```

To stop the application without removing its containers:

```bash
docker compose stop
```

To start previously stopped containers:

```bash
docker compose start
```

**Warning:** Do not use `docker compose down -v` for routine shutdowns. The `-v` option removes the project's associated named volumes and can permanently delete the local database data.

## Data persistence

PostgreSQL stores its data in the named volume `opsdesk-lab_postgres_data` in the default local Compose configuration.

The volume survives ordinary container recreation and `docker compose down`. It is removed by commands that explicitly delete the volume, such as `docker compose down -v`.

A persistent volume is not a backup. Important data should also be protected with a separate backup and recovery procedure.

## Security principles

- Never commit passwords, API keys, or real credentials.
- Keep `.env` local and excluded from Git.
- Use `.env.example` for configuration documentation without real secrets.
- Avoid exposing the database port publicly.
- Validate application inputs and handle errors explicitly.
- Maintain backups separately from Docker volumes.

## Current status

**Implemented and verified:**
- FastAPI application running in Docker.
- PostgreSQL service managed by Docker Compose.
- Database connection and readiness check.
- Application health check.
- Named volume for PostgreSQL persistence.
- Local container recreation test confirming data persistence.

**Planned:**
- IT incident creation and listing.
- Incident severity and status management.
- IT service inventory.
- Automated application and database integration tests.
- Backup and recovery procedures.

This project is being developed incrementally to demonstrate practical IT operations, API design, database management, and DevOps skills.
