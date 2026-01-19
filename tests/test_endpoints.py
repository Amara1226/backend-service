def test_welcome(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Aether" in r.text


def test_status(client):
    r = client.get("/status")
    assert r.status_code == 200
    j = r.json()
    assert "uptime_seconds" in j
    assert "active_sensors" in j


def test_ingest_unauthorized(client):
    r = client.post("/ingest", json={"sensor_id": "nope", "readings": {"pm25": 1, "pm10": 2, "no2": 3, "o3": 4}})
    assert r.status_code == 403


def test_ingest_ok(client):
    r = client.post("/ingest", json={"sensor_id": "sensor_ok_001", "readings": {"pm25": 12, "pm10": 22, "no2": 4, "o3": 33}})
    assert r.status_code == 200
    assert r.json()["sensor_id"] == "sensor_ok_001"


def test_map(client):
    r = client.get("/map")
    assert r.status_code == 200
    assert "plotly" in r.text.lower()


def test_history_ok(client):
    r = client.get("/history/sensor_ok_001")
    assert r.status_code == 200
    assert "rangeslider" in r.text.lower()
    
def test_history_invalid(client):
    r = client.get("/history/001")
    assert r.status_code == 404


def test_distribution_invalid_month(client):
    r = client.get("/distribution/2024/13")
    assert r.status_code == 400


def test_distribution_ok(client):
    r = client.get("/distribution/2024/1")
    assert r.status_code == 200
    assert ("barmode" in r.text.lower()) or ("stack" in r.text.lower())
