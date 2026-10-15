\# OpsDesk Lab



A containerized IT operations and incident management dashboard built as a practical portfolio project.



\## Project goal



OpsDesk Lab aims to provide a small web application for recording IT incidents, tracking their status, and maintaining an inventory of IT services.



The project focuses on practical skills relevant to IT support, systems administration, and junior DevOps roles.



\## Planned features



\- Create and list IT incidents.

\- Track incident status and severity.

\- Maintain a basic inventory of IT services.

\- Store application data in PostgreSQL.

\- Run the application and database using Docker Compose.

\- Add health checks and document deployment and troubleshooting procedures.



\## Technology stack



\- Python

\- FastAPI

\- PostgreSQL

\- Docker

\- Docker Compose

\- Git



\## Architecture



The application will use a small two-service architecture:



1\. \*\*Application service:\*\* a Python FastAPI application exposing the web interface and API.

2\. \*\*Database service:\*\* PostgreSQL storing incidents and service inventory data.



Docker Compose will manage both services on a private application network. PostgreSQL data will persist in a named Docker volume.



\## Repository structure



```text

app/                  Application source code

docs/                 Architecture and operational documentation

.env.example          Example configuration variables

compose.yaml          Multi-container application definition

Dockerfile            Application image definition

README.md             Project documentation

```



\## Planned deployment



Requirements:

\- Docker Desktop or Docker Engine with the Compose plugin.

\- Git.



The intended deployment command is:



```bash

docker compose up --build -d

```



The exact application URL, API endpoints, configuration variables, and troubleshooting commands will be documented after implementation and testing.



\## Security principles



\- Do not commit passwords, API keys, or real credentials.

\- Keep local environment variables in an untracked `.env` file.

\- Use a dedicated database user rather than the PostgreSQL superuser.

\- Avoid exposing the database port publicly.

\- Validate application inputs and handle errors explicitly.



\## Current status



\*\*Phase 1 — Project definition:\*\* repository structure, initial documentation, and architecture planning.



Implementation, testing, and deployment are pending.

