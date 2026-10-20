# Incident Model — OpsDesk Lab

## 1. Purpose

Define the initial incident data model and business rules before implementing database migrations or CRUD endpoints.

## 2. Scope

The first version supports incident creation, retrieval, updating, status changes, priority changes and deletion.

Out of scope: user authentication, incident assignment, comments, attachments, audit history, SLA management and automated prioritization.

## 3. Database table

Table: `incidents`

| Column | PostgreSQL type | Constraints |
|---|---|---|
| `id` | `UUID` | Primary key, generated automatically |
| `title` | `VARCHAR(160)` | NOT NULL, length 5–160 |
| `description` | `TEXT` | NOT NULL, length 10–5000 |
| `status` | `VARCHAR(20)` | NOT NULL, default `open`, allowlisted values |
| `priority` | `VARCHAR(10)` | NOT NULL, default `medium`, allowlisted values |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, generated at creation |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, updated on every modification |
| `resolved_at` | `TIMESTAMPTZ` | NULL until resolved |

All timestamps are timezone-aware and stored consistently in UTC.

## 4. Allowed statuses

- `open`: incident registered and awaiting resolution.
- `in_progress`: incident is being investigated or handled.
- `waiting`: work is blocked or awaiting information.
- `resolved`: a solution has been applied.
- `closed`: incident is considered finished.

Status transitions:

- `open` -> `in_progress`, `waiting`, `resolved`
- `in_progress` -> `waiting`, `resolved`
- `waiting` -> `in_progress`, `resolved`
- `resolved` -> `closed`, `open`
- `closed` -> `open`

The application must reject invalid transitions. Database constraints must also reject unknown status values.

## 5. Allowed priorities

- `low`: limited impact.
- `medium`: normal impact; default priority.
- `high`: significant impact requiring prompt attention.
- `critical`: critical service impact requiring immediate attention.

Database constraints must reject unknown priority values.

## 6. Validation and invariants

- `title` and `description` are required and must satisfy their length limits.
- `status` and `priority` must match the allowlists exactly.
- `updated_at` changes on every successful modification.
- `resolved_at` is populated when an incident becomes `resolved` or `closed`.
- `resolved_at` is cleared when an incident is reopened.
- UUIDs are generated automatically.
- Status-transition rules are enforced in the application service layer.
- Essential field and allowlist constraints are also enforced by PostgreSQL.

## 7. Initial architecture decisions

- PostgreSQL is the source of truth for incident records.
- FastAPI exposes the HTTP API.
- The existing Psycopg dependency is retained for the initial implementation.
- No ORM or migration dependency is added during this design task.
- Schema changes must be introduced through reviewed, version-controlled migrations.
- The application uses the dedicated `opsdesk_runtime` login role, which has no superuser, database/role creation, replication or RLS-bypass privileges. It has `CONNECT` on `opsdesk` and `USAGE` on `public`, but no `CREATE` privilege.
- No incident table or migration has been created yet. The initial `opsdesk_app` role remains the local cluster bootstrap superuser; the application uses `opsdesk_runtime` at runtime. Schema migrations must use a controlled administrative/migration role, followed by explicit runtime table grants.

## 8. Deferred decisions

Incident assignment, users, comments, attachments, audit history, pagination strategy and SLA rules are deferred until their requirements are defined.

## 9. Acceptance criteria

- The incident fields and PostgreSQL types are defined.
- Allowed statuses and priorities are documented.
- Invalid status transitions are specified.
- Validation and timestamp invariants are documented.
- Existing dependencies and configuration have been reviewed.
- This document defines the intended incident model; it does not implement the schema or migration. Local role and privilege changes are managed separately.
