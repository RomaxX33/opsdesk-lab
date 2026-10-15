\# OpsDesk Lab — Architecture



\## 1. Components



\### Application (`app`)



\- Language: Python

\- Framework: FastAPI

\- Responsibilities:

&#x20; - Expose application endpoints.

&#x20; - Validate incident and service data.

&#x20; - Read and write records through the database layer.

&#x20; - Provide health-check information.



\### Database (`db`)



\- Engine: PostgreSQL

\- Responsibilities:

&#x20; - Persist incident records.

&#x20; - Persist IT service inventory records.

&#x20; - Maintain data independently of application container restarts.



\## 2. Container architecture



Docker Compose manages two services:



\- `app`: builds from the repository's Dockerfile.

\- `db`: runs a pinned PostgreSQL major-version image.



Both services join a private Compose network. The application connects to PostgreSQL using the Compose service name `db`, not `localhost`.



\## 3. Data persistence



PostgreSQL stores its data in a named Docker volume. Recreating the application container must not erase database data.



\## 4. Configuration



Runtime configuration is provided through environment variables. A local `.env` file will contain development settings and must not be committed.



The `.env.example` file documents the required variable names using safe placeholder values.



\## 5. Networking



\- The application exposes its HTTP port to the local host for development.

\- PostgreSQL is accessible to the application over the private Compose network.

\- The database port is not published to the host by default.



\## 6. Reliability



\- PostgreSQL uses a health check.

\- Application startup waits for the database health condition.

\- The application exposes a health endpoint.

\- Logs are available through Docker Compose.



\## 7. Future improvements



\- Automated tests.

\- Database migrations.

\- CI workflow for linting and testing.

\- Reverse proxy and HTTPS for a later deployment environment.

\- Monitoring and backup documentation.



These are design intentions. Each feature will be marked as implemented only after it has been tested.

