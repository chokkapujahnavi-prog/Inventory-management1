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


def initialize_sales():
    if not os.path.exists(SALES_FILE):
        with open(SALES_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(SALES_FIELDS)


initialize_sales()


def read_products():
    products = []
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
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

        if product["Product ID"] == product_id:

            quantity_sold = int(input("Enter Quantity Sold: "))
            available_quantity = int(product["Quantity"])

            if quantity_sold <= 0:
                print("Invalid quantity.")
                return

            if quantity_sold > available_quantity:
                print("Insufficient stock.")
                return

            unit_price = float(product["Price"])
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

        for sale in reader:
            total_products += int(sale["Quantity Sold"])
            total_revenue += float(sale["Total Amount"])

    print("\n========== SALES SUMMARY ==========")
    print(f"Total Products Sold : {total_products}")
    print(f"Total Revenue       : ₹{total_revenue:.2f}")
    print("===================================")