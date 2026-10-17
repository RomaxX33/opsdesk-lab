import os

import psycopg
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row

app = FastAPI(
    title="OpsDesk Lab",
    description="Laboratorio de operaciones de sistemas y monitorización.",
    version="0.1.0",
)

DATABASE_URL = os.environ["DATABASE_URL"]


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
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "database": "unavailable",
                "error": type(exc).__name__,
            },
        ) from exc
