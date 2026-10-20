from fastapi.testclient import TestClient
from app_final import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "max_temp_threshold" in data


def test_add_and_list_readings():
    payload = {
        "sensor_id": "test-sensor-1",
        "location": "Lab",
        "temperature": 42.0,
        "humidity": 30.0,
    }
    post_resp = client.post("/readings", json=payload)
    assert post_resp.status_code == 201
    assert post_resp.json()["alert"] is True

    get_resp = client.get("/readings", params={"location": "Lab"})
    assert get_resp.status_code == 200
    assert get_resp.json()["count"] >= 1


def test_sensor_stats_parameter():
    response = client.get("/sensors/srv-01/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["sensor_id"] == "srv-01"
    assert "avg_temperature" in data


def test_sensor_stats_not_found_error():
    response = client.get("/sensors/unknown-sensor-999/stats")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
