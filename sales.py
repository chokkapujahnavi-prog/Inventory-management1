import csv
import os
from datetime import datetime

PRODUCTS_FILE = "products.csv"
SALES_FILE = "sales.csv"

SALES_FIELDS = [
    "Date",
    "Product ID",
    "Product Name",
    "Quantity Sold",
    "Unit Price",
    "Total Amount"
]


def ensure_csv_header(file_path, fieldnames):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(fieldnames)


def initialize_sales():
    ensure_csv_header(SALES_FILE, SALES_FIELDS)


initialize_sales()


def read_products():
    products = []
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not any(row.values()):
                    continue
                products.append(row)
    return products


def write_products(products):
    fieldnames = [
        "Product ID",
        "Product Name",
        "Category",
        "Price",
        "Quantity",
        "Supplier"
    ]

    with open(PRODUCTS_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)


def record_sale():
    products = read_products()

    product_id = input("Enter Product ID: ")

    for product in products:

        if product["Product ID"].strip() == product_id.strip():
            quantity_text = input("Enter Quantity Sold: ").strip()
            try:
                quantity_sold = int(quantity_text)
                if quantity_sold <= 0:
                    raise ValueError
            except ValueError:
                print("Invalid quantity.")
                return

            try:
                available_quantity = int(product["Quantity"])
            except ValueError:
                print("Invalid product stock value.")
                return

            if quantity_sold > available_quantity:
                print("Insufficient stock.")
                return

            try:
                unit_price = float(product["Price"])
            except ValueError:
                print("Invalid product price.")
                return

            total_amount = unit_price * quantity_sold

            product["Quantity"] = str(
                available_quantity - quantity_sold
            )

            write_products(products)

            with open(SALES_FILE, "a", newline="") as file:
                writer = csv.writer(file)

                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    product["Product ID"],
                    product["Product Name"],
                    quantity_sold,
                    unit_price,
                    total_amount
                ])

            print("\nSale Recorded Successfully!")
            print(f"Total Amount = ₹{total_amount:.2f}")
            return

    print("Product not found.")


def sales_summary():

    if not os.path.exists(SALES_FILE):
        print("No sales found.")
        return

    total_products = 0
    total_revenue = 0

    with open(SALES_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            print("No sales found.")
            return

        for sale in reader:
            try:
                total_products += int(sale["Quantity Sold"])
                total_revenue += float(sale["Total Amount"])
            except (ValueError, KeyError, TypeError):
                continue

    print("\n========== SALES SUMMARY ==========")
    print(f"Total Products Sold : {total_products}")
    print(f"Total Revenue       : ₹{total_revenue:.2f}")
    print("===================================")