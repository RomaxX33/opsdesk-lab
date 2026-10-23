import uuid

import pytest


def test_create_and_get_incident(client):
    payload = {
        "title": "Prueba automatizada CRUD",
        "description": "Verificando ciclo completo de incidencias con descripción válida",
        "priority": "high",
    }

    response = client.post("/incidents", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["priority"] == "high"
    assert data["status"] == "open"
    assert "id" in data

    get_response = client.get(f"/incidents/{data['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == data["id"]


def test_create_strips_surrounding_whitespace(client):
    response = client.post(
        "/incidents",
        json={
            "title": "  Título con espacios  ",
            "description": "  Descripción válida para la prueba automatizada  ",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Título con espacios"
    assert data["description"] == "Descripción válida para la prueba automatizada"


def test_list_incidents(client):
    response = client.get("/incidents")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_and_delete_incident(client):
    created = client.post(
        "/incidents",
        json={
            "title": "Incidencia temporal",
            "description": "Descripción temporal suficientemente larga para validar",
            "priority": "low",
        },
    )

    assert created.status_code == 201
    incident_id = created.json()["id"]

    patch_response = client.patch(
        f"/incidents/{incident_id}",
        json={"status": "in_progress", "priority": "medium"},
    )

    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == "in_progress"
    assert patch_response.json()["priority"] == "medium"

    delete_response = client.delete(f"/incidents/{incident_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/incidents/{incident_id}")
    assert get_response.status_code == 404


@pytest.mark.parametrize(
    "overrides",
    [
        {"title": "abc"},
        {"description": "corta"},
        {"priority": "urgent"},
    ],
)
def test_create_rejects_invalid_input(client, overrides):
    payload = {
        "title": "Título válido de prueba",
        "description": "Descripción válida para comprobar las validaciones",
        "priority": "medium",
    }
    payload.update(overrides)

    response = client.post("/incidents", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": None},
        {"status": "unknown"},
        {"unexpected_field": "not allowed"},
    ],
)
def test_update_rejects_invalid_input(client, payload):
    incident_id = str(uuid.uuid4())

    response = client.patch(f"/incidents/{incident_id}", json=payload)

    assert response.status_code == 422


def test_error_handling(client):
    invalid_uuid_response = client.patch(
        "/incidents/uuid-invalido",
        json={"status": "open"},
    )
    assert invalid_uuid_response.status_code == 422

    missing_id = str(uuid.uuid4())
    missing_response = client.get(f"/incidents/{missing_id}")
    assert missing_response.status_code == 404
