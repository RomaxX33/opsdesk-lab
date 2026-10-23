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
opsdesk-lab/
|-- app/
|   |-- __init__.py
|   `-- main.py
|-- docs/
|   `-- architecture.md
|-- migrations/
|   |-- 001_create_incidents.sql
|   |-- 002_incidents_update_permissions.sql
|   `-- 003_incidents_delete_permissions.sql
|-- tests/
|   |-- conftest.py
|   |-- init-test-db.sql
|   `-- test_incidents.py
|-- .env.example
|-- .gitignore
|-- compose.test.yaml
|-- compose.yaml
|-- Dockerfile
|-- README.md
`-- requirements.txt
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

## Automated tests

The integration tests use a dedicated PostgreSQL service (`opsdesk-test-db`) and database (`opsdesk_test`). A test guard blocks execution unless `DATABASE_URL` points to that host and database.

The suite currently contains 12 test cases covering incident creation, retrieval, listing, updating, deletion, input validation, whitespace normalization, and selected HTTP errors. Test-created rows are cleaned up after each test. This cleanup is not transaction rollback isolation.

### Run the tests

Run these commands from the project root in PowerShell. Apply the migrations only when setting up a fresh test database or after intentionally recreating the test database.

```powershell
docker compose -f .\compose.yaml -f .\compose.test.yaml up -d opsdesk-test-db

$composeFiles = @("-f", ".\compose.yaml", "-f", ".\compose.test.yaml")

$migrations = @(
    "001_create_incidents.sql",
    "002_incidents_update_permissions.sql",
    "003_incidents_delete_permissions.sql"
)

foreach ($migration in $migrations) {
    $source = Join-Path $PWD "migrations\$migration"
    $destination = "/tmp/$migration"

    if (-not (Test-Path $source)) {
        throw "Migration not found: $source"
    }

    docker compose @composeFiles cp $source "opsdesk-test-db:$destination"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to copy $migration. Stopping."
    }

    docker compose @composeFiles exec -T opsdesk-test-db `
        psql -v ON_ERROR_STOP=1 -U opsdesk_test_admin `
        -d opsdesk_test -f $destination

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to apply $migration. Stopping."
    }
}

docker compose @composeFiles exec -T `
    -e DATABASE_URL=postgresql://opsdesk_runtime:opsdesk-test-runtime-local-only@opsdesk-test-db:5432/opsdesk_test `
    app python -m pytest -v /app/tests
```

The test database is separate from the development database and has no named persistent volume. Never point the test suite at the development `db` service.

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
- Automated integration tests against an isolated PostgreSQL test database (12 test cases passed in the latest run).

**Planned:**
- Backup and recovery procedures.
- IT service inventory.

This project is being developed incrementally to demonstrate practical IT operations, API design, database management, and DevOps skills.

## Incidents API

The incidents API supports creating, listing, and retrieving incidents. All endpoints return JSON.

### Incident model

| Field | Description |
|---|---|
| `id` | UUID generated by PostgreSQL |
| `title` | Required; 5–160 characters |
| `description` | Required; 10–5000 characters |
| `status` | `open`, `in_progress`, `waiting`, `resolved`, `closed` |
| `priority` | `low`, `medium`, `high`, `critical` |
| `created_at` | Creation timestamp in UTC |
| `updated_at` | Last update timestamp in UTC |
| `resolved_at` | Resolution timestamp, or `null` |

### Create an incident

`POST /incidents`

Example request:

```json
{
  "title": "VPN access unavailable",
  "description": "Remote users cannot establish a VPN connection.",
  "priority": "high"
}
```

Successful response: `201 Created`. The response includes the generated UUID, the default status (`open`), timestamps, and the submitted fields.

Invalid or missing fields return `422 Unprocessable Entity`. Database connection failures return `503 Service Unavailable`; other database operation errors return `500 Internal Server Error`.

### List incidents

`GET /incidents`

Supported query parameters:

| Parameter | Default | Constraints |
|---|---:|---|
| `limit` | `50` | 1–100 |
| `offset` | `0` | 0 or greater |

Example:

`GET /incidents?limit=10&offset=0`

Successful response: `200 OK`, with a JSON array ordered by creation time descending. The UUID is used as a secondary ordering key.

Invalid pagination parameters return `422 Unprocessable Entity`. Database connection failures return `503 Service Unavailable`; other database operation errors return `500 Internal Server Error`.

### Retrieve one incident

`GET /incidents/{incident_id}`

Example:

`GET /incidents/d6ac9e18-c47f-46d6-8a72-fa10457978c0`

A successful request returns `200 OK` and the incident object.

- `404 Not Found`: the UUID is valid, but no incident exists with that ID.
- `422 Unprocessable Entity`: the path parameter is not a valid UUID.
- `503 Service Unavailable`: the database connection is unavailable.
- `500 Internal Server Error`: another database operation fails.

### Update an incident

Endpoint: PATCH /incidents/{incident_id}

Updates one or more fields of an existing incident. The incident ID must be a valid UUID.

Supported fields:
- title: 5 to 160 characters after trimming surrounding whitespace.
- description: 10 to 5000 characters after trimming surrounding whitespace.
- status: open, in_progress, waiting, resolved, or closed.
- priority: low, medium, high, or critical.

At least one field must be provided. Fields cannot be null. Unknown fields and invalid values are rejected.

Status transitions:
- open, in_progress, and waiting can transition to any supported status.
- resolved can transition to open, in_progress, resolved, or closed.
- closed can only remain closed.

A successful update returns HTTP 200 and the updated incident as JSON.

Error responses:
- 404: the incident does not exist.
- 422: invalid UUID, invalid fields, empty update, null field, or disallowed status transition.
- 503: database temporarily unavailable.
- 500: unexpected database error.

### Delete an incident

Endpoint: DELETE /incidents/{incident_id}

Deletes an existing incident. The incident ID must be a valid UUID.

A successful deletion returns HTTP 204 with an empty response body.

Error responses:
- 404: the incident does not exist.
- 422: invalid UUID.
- 503: database temporarily unavailable.
- 500: unexpected database error.

### Manual verification results

The following behaviors have been manually verified against the running application and PostgreSQL:

- Creating an incident returns `201 Created` and persists the record.
- Invalid incident input returns `422 Unprocessable Entity`.
- Listing and pagination return the persisted incident.
- A pagination limit of `101` returns `422 Unprocessable Entity`.
- Retrieving an existing incident returns `200 OK`.
- Retrieving a valid but nonexistent UUID returns `404 Not Found`.
- An invalid UUID returns `422 Unprocessable Entity`.
- The readiness endpoint confirms database connectivity.
