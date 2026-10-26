
# Inventory Management System

A Python REST API and command-line inventory management application built
with Flask for the Moringa summative lab.

## Features

- Retrieve all inventory items and individual items.
- Create, update, and delete inventory items.
- Search OpenFoodFacts products by name or barcode.
- Import external products into the inventory.
- Manage inventory through a command-line interface.
- Automated tests using pytest and unittest.mock.

## Technologies

- Python
- Flask
- Requests
- pytest
- OpenFoodFacts API

## Setup

Clone the repository, then enter the project directory.

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the API

```bash
python app.py
```

The API runs at http://127.0.0.1:5000.

## Run the CLI

Keep the API running in one terminal. In another terminal, activate
the virtual environment and run:

```bash
python cli.py
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /inventory | List all items |
| GET | /inventory/<id> | Retrieve one item |
| POST | /inventory | Create an item |
| PATCH | /inventory/<id> | Update an item |
| DELETE | /inventory/<id> | Delete an item |
| GET | /products/barcode/<barcode> | Search by barcode |
| GET | /products/search?name=milk | Search by name |
| POST | /products/import | Import a product |

## Run tests

```bash
python -m pytest -v
```

## Data storage

Inventory data is stored in memory for this lab and resets when the
Flask application restarts.
