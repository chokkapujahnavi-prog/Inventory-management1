import csv
import os

PRODUCTS_FILE = "products.csv"
LOW_STOCK_THRESHOLD = 10

FIELDS = [
    "Product ID",
    "Product Name",
    "Category",
    "Price",
    "Quantity",
    "Supplier"
]


def ensure_csv_header(file_path, fieldnames):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(fieldnames)


def initialize_products():
    ensure_csv_header(PRODUCTS_FILE, FIELDS)


initialize_products()


def read_products():
    products = []
    with open(PRODUCTS_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not any(row.values()):
                continue
            products.append(row)
    return products


def write_products(products):
    with open(PRODUCTS_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(products)


def add_product():
    products = read_products()

    product_id = input("Enter Product ID: ").strip()
    if not product_id:
        print("Error: Product ID is required.")
        return

    for product in products:
        if product["Product ID"].strip().lower() == product_id.lower():
            print("Error: Product ID already exists.")
            return

    name = input("Enter Product Name: ").strip()
    if not name:
        print("Error: Product Name is required.")
        return

    category = input("Enter Category: ").strip()
    price_text = input("Enter Price: ").strip()
    quantity_text = input("Enter Quantity: ").strip()
    supplier = input("Enter Supplier Name: ").strip()

    try:
        price = float(price_text)
        quantity = int(quantity_text)
        if price < 0 or quantity < 0:
            raise ValueError
    except ValueError:
        print("Error: Price and Quantity must be valid non-negative numbers.")
        return

    products.append({
        "Product ID": product_id,
        "Product Name": name,
        "Category": category,
        "Price": str(price),
        "Quantity": str(quantity),
        "Supplier": supplier
    })

    write_products(products)
    print("Product added successfully.")


def view_products():
    products = read_products()

    if not products:
        print("No products found.")
        return

    print("\n" + "-" * 90)
    print("{:<10} {:<20} {:<15} {:<10} {:<10} {:<20}".format(
        "ID", "Name", "Category", "Price", "Qty", "Supplier"))
    print("-" * 90)

    for product in products:
        print("{:<10} {:<20} {:<15} {:<10} {:<10} {:<20}".format(
            product["Product ID"],
            product["Product Name"],
            product["Category"],
            product["Price"],
            product["Quantity"],
            product["Supplier"]
        ))


def search_product():
    products = read_products()

    choice = input("Search by (1-ID / 2-Name): ")

    if choice == "1":
        value = input("Enter Product ID: ")
        key = "Product ID"
    elif choice == "2":
        value = input("Enter Product Name: ")
        key = "Product Name"
    else:
        print("Invalid choice.")
        return

    found = False

    for product in products:
        if product[key].lower() == value.lower():
            print("\nProduct Found")
            print(product)
            found = True

    if not found:
        print("Product not found.")


def update_product():
    products = read_products()

    product_id = input("Enter Product ID to update: ")

    for product in products:
        if product["Product ID"] == product_id:

            print("Leave blank to keep old value.")

            name = input(f"Name ({product['Product Name']}): ")
            category = input(f"Category ({product['Category']}): ")
            price = input(f"Price ({product['Price']}): ")
            quantity = input(f"Quantity ({product['Quantity']}): ")

            if name:
                product["Product Name"] = name.strip()
            if category:
                product["Category"] = category.strip()
            if price:
                try:
                    product["Price"] = str(float(price.strip()))
                except ValueError:
                    print("Invalid price value.")
                    return
            if quantity:
                try:
                    product["Quantity"] = str(int(quantity.strip()))
                except ValueError:
                    print("Invalid quantity value.")
                    return

            write_products(products)
            print("Product updated successfully.")
            return

    print("Product not found.")


def delete_product():
    products = read_products()

    product_id = input("Enter Product ID to delete: ")

    updated_products = [
        product for product in products
        if product["Product ID"] != product_id
    ]

    if len(updated_products) == len(products):
        print("Product not found.")
        return

    write_products(updated_products)
    print("Product deleted successfully.")


def add_stock():
    products = read_products()

    product_id = input("Enter Product ID: ")

    for product in products:
        if product["Product ID"] == product_id:
            qty_text = input("Enter quantity to add: ").strip()
            try:
                qty = int(qty_text)
                if qty <= 0:
                    raise ValueError
            except ValueError:
                print("Error: Quantity must be a positive integer.")
                return

            try:
                current_qty = int(product["Quantity"])
            except ValueError:
                current_qty = 0

            product["Quantity"] = str(current_qty + qty)

            write_products(products)
            print("Stock updated successfully.")
            return

    print("Product not found.")


def low_stock_alert():
    products = read_products()

    print("\nLow Stock Products")
    print("-" * 50)

    found = False

    for product in products:
        if int(product["Quantity"]) < LOW_STOCK_THRESHOLD:
            print(
                f"{product['Product ID']} - "
                f"{product['Product Name']} "
                f"(Qty: {product['Quantity']})"
            )
            found = True

    if not found:
        print("No low stock products.")