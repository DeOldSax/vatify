from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_rates_de_ok():
    r = client.get("/rates/DE")
    assert r.status_code == 200
    data = r.json()
    assert data["country"] == "DE"
    assert data["standard_rate"] == 19.0
    assert any(rr["rate"] == 7.0 for rr in data["reduced_rates"])

def test_get_rates_unknown_country():
    r = client.get("/rates/XX")
    assert r.status_code == 404

def test_get_rates_with_date_filter():
    r = client.get("/rates/FR?date=2024-01-15") # wählt den letzten Eintrag ≤ 2024-01-15.
    assert r.status_code == 200
    assert r.json()["country"] == "FR"
