import os
from datetime import datetime
from typing import Literal
from uuid import UUID

import psycopg
from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field, field_validator, model_validator
from psycopg.rows import dict_row


app = FastAPI(
    title="OpsDesk Lab",
    description="Laboratorio de operaciones de sistemas y monitorización.",
    version="0.1.0",
)

DATABASE_URL = os.environ["DATABASE_URL"]

IncidentStatus = Literal[
    "open",
    "in_progress",
    "waiting",
    "resolved",
    "closed",
]

IncidentPriority = Literal[
    "low",
    "medium",
    "high",
    "critical",
]


class IncidentCreate(BaseModel):
    title: str = Field(min_length=5, max_length=160)
    description: str = Field(min_length=10, max_length=5000)
    priority: IncidentPriority = "medium"

    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_text(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class IncidentRead(BaseModel):
    id: UUID
    title: str
    description: str
    status: IncidentStatus
    priority: IncidentPriority
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


@app.get("/")
def root():
    return {
        "application": "OpsDesk Lab",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def readiness():
    try:
        with psycopg.connect(
            DATABASE_URL,
            connect_timeout=3,
            row_factory=dict_row,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS result")
                result = cursor.fetchone()

        return {
            "status": "ready",
            "database": "connected",
            "check": result["result"],
        }
    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "database": "unavailable",
            },
        ) from None


@app.post(
    "/incidents",
    response_model=IncidentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(payload: IncidentCreate):
    try:
        with psycopg.connect(
            DATABASE_URL,
            connect_timeout=3,
            row_factory=dict_row,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO public.incidents (
                        title,
                        description,
                        priority
                    )
                    VALUES (%s, %s, %s)
                    RETURNING
                        id,
                        title,
                        description,
                        status,
                        priority,
                        created_at,
                        updated_at,
                        resolved_at
                    """,
                    (
                        payload.title,
                        payload.description,
                        payload.priority,
                    ),
                )
                incident = cursor.fetchone()

        return incident

    except psycopg.OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        ) from exc
@app.get(
    "/incidents",
    response_model=list[IncidentRead],
)
def list_incidents(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    try:
        with psycopg.connect(
            DATABASE_URL,
            connect_timeout=3,
            row_factory=dict_row,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        title,
                        description,
                        status,
                        priority,
                        created_at,
                        updated_at,
                        resolved_at
                    FROM public.incidents
                    ORDER BY created_at DESC, id DESC
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
                incidents = cursor.fetchall()

        return incidents

    except psycopg.OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        ) from exc


@app.get(
    "/incidents/{incident_id}",
    response_model=IncidentRead,
)
def get_incident(incident_id: UUID):
    try:
        with psycopg.connect(
            DATABASE_URL,
            connect_timeout=3,
            row_factory=dict_row,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        title,
                        description,
                        status,
                        priority,
                        created_at,
                        updated_at,
                        resolved_at
                    FROM public.incidents
                    WHERE id = %s
                    """,
                    (incident_id,),
                )
                incident = cursor.fetchone()

        if incident is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )

        return incident

    except psycopg.OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        ) from exc
class IncidentUpdate(BaseModel):
    model_config = {"extra": "forbid"}

    title: str = Field(default=None, min_length=5, max_length=160)
    description: str = Field(default=None, min_length=10, max_length=5000)
    status: IncidentStatus = None
    priority: IncidentPriority = None

    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_text(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Fields cannot be null")
        return self


@app.patch(
    "/incidents/{incident_id}",
    response_model=IncidentRead,
)
def update_incident(incident_id: UUID, payload: IncidentUpdate):
    allowed_transitions = {
        "open": {"open", "in_progress", "waiting", "resolved", "closed"},
        "in_progress": {"open", "in_progress", "waiting", "resolved", "closed"},
        "waiting": {"open", "in_progress", "waiting", "resolved", "closed"},
        "resolved": {"open", "in_progress", "resolved", "closed"},
        "closed": {"closed"},
    }

    updates = payload.model_dump(exclude_unset=True)

    try:
        with psycopg.connect(
            DATABASE_URL,
            connect_timeout=3,
            row_factory=dict_row,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, status
                    FROM public.incidents
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (incident_id,),
                )
                current = cursor.fetchone()

                if current is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Incident not found",
                    )

                new_status = updates.get("status", current["status"])

                if new_status not in allowed_transitions[current["status"]]:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Invalid incident status transition",
                    )

                assignments = []
                values = []

                for field, value in updates.items():
                    assignments.append(f"{field} = %s")
                    values.append(value)

                values.append(incident_id)

                cursor.execute(
                    f"""
                    UPDATE public.incidents
                    SET {", ".join(assignments)}
                    WHERE id = %s
                    RETURNING
                        id,
                        title,
                        description,
                        status,
                        priority,
                        created_at,
                        updated_at,
                        resolved_at
                    """,
                    values,
                )
                incident = cursor.fetchone()

        return incident

    except HTTPException:
        raise
    except psycopg.OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        ) from exc

@app.delete(
    "/incidents/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_incident(incident_id: UUID) -> Response:
    try:
        with psycopg.connect(
            DATABASE_URL,
            connect_timeout=3,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM public.incidents
                    WHERE id = %s
                    RETURNING id
                    """,
                    (incident_id,),
                )
                deleted = cursor.fetchone()

                if deleted is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Incident not found",
                    )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException:
        raise
    except psycopg.OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        ) from exc
