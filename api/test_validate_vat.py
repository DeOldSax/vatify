import pytest
from fastapi.testclient import TestClient

# Importiere deine FastAPI-App
from main import app

client = TestClient(app)

# Beispiel-USt-IDs
VALID_VATS = [
    ("DE", "DE811907980"),   # BMW AG
    ("DE", "DE136695976"),   # Deutsche Telekom AG
    ("FR", "FR40303265045"), # Airbus
    ("IT", "IT00743110157"), # Ferrari
]

INVALID_VATS = [
    ("DE", "DE123456789"),
    ("FR", "FR12345678901"),
    ("IT", "IT00000000000"),
]


@pytest.mark.parametrize("country,vat_number", VALID_VATS)
def test_valid_vat_numbers(country, vat_number):
    response = client.post(
        "/validate-vat",
        json={"vat_number": vat_number},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["country_code"] == country
    assert data["vat_number"].startswith(country)
    assert data["valid"] is True
    assert "request_date" in data


@pytest.mark.parametrize("country,vat_number", INVALID_VATS)
def test_invalid_vat_numbers(country, vat_number):
    response = client.post(
        "/validate-vat",
        json={"vat_number": vat_number},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["country_code"] == country
    assert data["vat_number"].startswith(country)
    assert data["valid"] is False
