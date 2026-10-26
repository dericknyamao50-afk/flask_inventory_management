
import pytest
from unittest.mock import patch
from app import app, inventory


@pytest.fixture
def client():
    app.config["TESTING"] = True
    original_inventory = [item.copy() for item in inventory]

    with app.test_client() as test_client:
        yield test_client

    inventory.clear()
    inventory.extend(original_inventory)


def test_get_all_inventory(client):
    response = client.get("/inventory")

    assert response.status_code == 200
    assert len(response.get_json()) >= 2


def test_get_single_item(client):
    response = client.get("/inventory/1")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Organic Almond Milk"


def test_get_missing_item(client):
    response = client.get("/inventory/9999")

    assert response.status_code == 404


def test_create_item(client):
    response = client.post(
        "/inventory",
        json={
            "name": "Mango Juice",
            "price": 120,
            "stock": 10
        }
    )

    assert response.status_code == 201
    assert response.get_json()["name"] == "Mango Juice"


def test_create_item_with_invalid_data(client):
    response = client.post(
        "/inventory",
        json={"name": "Mango Juice"}
    )

    assert response.status_code == 400


def test_update_item(client):
    response = client.patch(
        "/inventory/1",
        json={"stock": 25}
    )

    assert response.status_code == 200
    assert response.get_json()["stock"] == 25


def test_delete_item(client):
    response = client.delete("/inventory/2")

    assert response.status_code == 200
    assert client.get("/inventory/2").status_code == 404


@patch("app.fetch_product")
def test_barcode_lookup(mock_fetch, client):
    mock_fetch.return_value = {
        "barcode": "1234567890123",
        "name": "Test Product",
        "brand": "Test Brand",
        "ingredients": "Water",
        "image_url": ""
    }

    response = client.get("/products/barcode/1234567890123")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Test Product"
    mock_fetch.assert_called_once_with(barcode="1234567890123")


@patch("app.fetch_product")
def test_import_external_product(mock_fetch, client):
    mock_fetch.return_value = {
        "barcode": "5555555555555",
        "name": "Imported Product",
        "brand": "Test Brand",
        "ingredients": "Water",
        "image_url": ""
    }

    response = client.post(
        "/products/import",
        json={"barcode": "5555555555555"}
    )

    assert response.status_code == 201
    assert response.get_json()["name"] == "Imported Product"
    mock_fetch.assert_called_once_with(barcode="5555555555555")
