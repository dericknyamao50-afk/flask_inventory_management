
import requests

BASE_URL = "http://127.0.0.1:5000"


def display_inventory():
    try:
        response = requests.get(f"{BASE_URL}/inventory", timeout=5)
        response.raise_for_status()

        items = response.json()
        if not items:
            print("Inventory is empty.")
            return

        for item in items:
            print(
                f"ID: {item['id']} | Name: {item['name']} | "
                f"Price: {item['price']} | Stock: {item['stock']}"
            )
    except requests.RequestException as error:
        print(f"Could not connect to the API: {error}")


def add_item():
    try:
        name = input("Product name: ").strip()
        price = float(input("Price: "))
        stock = int(input("Stock quantity: "))

        if not name or price < 0 or stock < 0:
            print("Enter a name and non-negative price and stock.")
            return

        item = {
            "name": name,
            "price": price,
            "stock": stock
        }

        response = requests.post(
            f"{BASE_URL}/inventory",
            json=item,
            timeout=5
        )

        print(response.status_code, response.json())

    except ValueError:
        print("Price must be numeric and stock must be a whole number.")
    except requests.RequestException as error:
        print(f"Could not connect to the API: {error}")


def view_item():
    try:
        item_id = int(input("Enter item ID: "))
        response = requests.get(
            f"{BASE_URL}/inventory/{item_id}",
            timeout=5
        )
        print(response.status_code, response.json())
    except ValueError:
        print("Enter a valid integer ID.")
    except requests.RequestException as error:
        print(f"Could not connect to the API: {error}")


def update_item():
    try:
        item_id = int(input("Enter item ID to update: "))
        print("Enter only the fields you want to change.")
        data = {}

        name = input("New name (leave blank to skip): ").strip()
        price = input("New price (leave blank to skip): ").strip()
        stock = input("New stock (leave blank to skip): ").strip()

        if name:
            data["name"] = name
        if price:
            data["price"] = float(price)
        if stock:
            data["stock"] = int(stock)

        if not data:
            print("No changes entered.")
            return

        response = requests.patch(
            f"{BASE_URL}/inventory/{item_id}",
            json=data,
            timeout=5
        )
        print(response.status_code, response.json())

    except ValueError:
        print("ID and stock must be integers; price must be numeric.")
    except requests.RequestException as error:
        print(f"Could not connect to the API: {error}")


def delete_item():
    try:
        item_id = int(input("Enter item ID to delete: "))
        confirm = input("Are you sure? (y/n): ").lower()

        if confirm != "y":
            print("Deletion cancelled.")
            return

        response = requests.delete(
            f"{BASE_URL}/inventory/{item_id}",
            timeout=5
        )
        print(response.status_code, response.json())

    except ValueError:
        print("Enter a valid integer ID.")
    except requests.RequestException as error:
        print(f"Could not connect to the API: {error}")


def search_product():
    name = input("Product name to search on OpenFoodFacts: ").strip()

    if not name:
        print("Product name cannot be empty.")
        return

    try:
        response = requests.get(
            f"{BASE_URL}/products/search",
            params={"name": name},
            timeout=15
        )
        print(response.status_code, response.json())
    except requests.RequestException as error:
        print(f"Request failed: {error}")


def import_product():
    barcode = input("Barcode (leave blank to search by name): ").strip()
    name = ""

    if not barcode:
        name = input("Product name: ").strip()

    if not barcode and not name:
        print("Enter a barcode or product name.")
        return

    data = {"barcode": barcode} if barcode else {"name": name}

    try:
        response = requests.post(
            f"{BASE_URL}/products/import",
            json=data,
            timeout=15
        )
        print(response.status_code, response.json())
    except requests.RequestException as error:
        print(f"Request failed: {error}")


def main():
    while True:
        print("\n=== INVENTORY MANAGEMENT SYSTEM ===")
        print("1. View all inventory")
        print("2. View one item")
        print("3. Add item")
        print("4. Update item")
        print("5. Delete item")
        print("6. Search OpenFoodFacts")
        print("7. Import external product")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        actions = {
            "1": display_inventory,
            "2": view_item,
            "3": add_item,
            "4": update_item,
            "5": delete_item,
            "6": search_product,
            "7": import_product
        }

        if choice == "0":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
