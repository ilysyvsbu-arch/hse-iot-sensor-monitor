import copy

import pytest
from fastapi.testclient import TestClient

import app_final
from app_final import app


INITIAL_READINGS = [
    {
        "sensor_id": "srv-01",
        "location": "Server Room",
        "temperature": 22.5,
        "humidity": 40.0,
        "alert": False,
    },
    {
        "sensor_id": "srv-02",
        "location": "Server Room",
        "temperature": 38.0,
        "humidity": 35.0,
        "alert": True,
    },
    {
        "sensor_id": "off-01",
        "location": "Office 101",
        "temperature": 24.0,
        "humidity": 50.0,
        "alert": False,
    },
]

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_readings_db(monkeypatch):
    """Изолируем данные каждого теста."""
    monkeypatch.setattr(
        app_final,
        "READINGS_DB",
        copy.deepcopy(INITIAL_READINGS),
    )
    monkeypatch.setattr(app_final, "MAX_TEMP_THRESHOLD", 35.0)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version():
    response = client.get("/version")

    assert response.status_code == 200

    data = response.json()
    assert data["version"]
    assert data["max_temp_threshold"] == 35.0


def test_list_sensors():
    response = client.get("/sensors")

    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 3

    sensor_ids = {
        item["sensor_id"] for item in data["items"]
    }
    assert sensor_ids == {"srv-01", "srv-02", "off-01"}


def test_add_and_list_readings():
    payload = {
        "sensor_id": "test-sensor-1",
        "location": "Lab",
        "temperature": 42.0,
        "humidity": 30.0,
    }

    post_response = client.post("/readings", json=payload)

    assert post_response.status_code == 201
    assert post_response.json()["alert"] is True

    get_response = client.get(
        "/readings",
        params={"location": "Lab"},
    )

    assert get_response.status_code == 200

    data = get_response.json()
    assert data["count"] == 1
    assert data["items"][0]["sensor_id"] == "test-sensor-1"


def test_filter_alert_only():
    response = client.get(
        "/readings",
        params={"alert_only": "true"},
    )

    assert response.status_code == 200

    items = response.json()["items"]
    assert items
    assert all(item["alert"] is True for item in items)


def test_invalid_reading():
    payload = {
        "sensor_id": "test-sensor-2",
        "location": "Lab",
        "temperature": 151.0,
        "humidity": 30.0,
    }

    response = client.post("/readings", json=payload)

    assert response.status_code == 422


def test_sensor_stats_parameter():
    response = client.get("/sensors/srv-01/stats")

    assert response.status_code == 200

    data = response.json()
    assert data["sensor_id"] == "srv-01"
    assert data["readings_count"] == 1
    assert data["min_temperature"] == 22.5
    assert data["max_temperature"] == 22.5
    assert data["avg_temperature"] == 22.5
    assert data["has_alerts"] is False


def test_sensor_stats_not_found_error():
    response = client.get(
        "/sensors/unknown-sensor-999/stats"
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
