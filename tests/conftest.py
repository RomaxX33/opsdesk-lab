import os
from urllib.parse import urlsplit

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def require_isolated_test_database():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.fail("Bloqueado: DATABASE_URL no está definida.")

    parsed = urlsplit(db_url)
    if (
        parsed.hostname != "opsdesk-test-db"
        or parsed.path.lstrip("/") != "opsdesk_test"
    ):
        pytest.fail(
            "Bloqueado: las pruebas solo pueden ejecutarse contra "
            "opsdesk_test en el host opsdesk-test-db."
        )


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def cleanup_test_incidents():
    db_url = os.environ["DATABASE_URL"]

    with psycopg.connect(db_url) as conn:
        baseline_ids = {
            row[0]
            for row in conn.execute(
                "SELECT id FROM public.incidents"
            ).fetchall()
        }

    try:
        yield
    finally:
        with psycopg.connect(db_url) as conn:
            current_ids = {
                row[0]
                for row in conn.execute(
                    "SELECT id FROM public.incidents"
                ).fetchall()
            }

            new_ids = current_ids - baseline_ids

            for incident_id in new_ids:
                conn.execute(
                    "DELETE FROM public.incidents WHERE id = %s",
                    (incident_id,),
                )
