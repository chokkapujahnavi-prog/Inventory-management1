import csv
import os
from collections import Counter

PRODUCTS_FILE = "products.csv"
SALES_FILE = "sales.csv"


def inventory_report():
    """Display inventory statistics"""

    if not os.path.exists(PRODUCTS_FILE):
        print("Products file not found.")
        return

    with open(PRODUCTS_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        products = list(reader)

    if not products:
        print("No products available.")
        return

    total_products = len(products)
    total_categories = len(set(p["Category"] for p in products))
    total_stock = sum(int(p["Quantity"]) for p in products)

    print("\n" + "=" * 40)
    print("       INVENTORY REPORT")
    print("=" * 40)
    print(f"Total Products    : {total_products}")
    print(f"Total Categories  : {total_categories}")
    print(f"Available Stock   : {total_stock}")
    print("=" * 40)


def sales_report():
    """Display sales statistics"""

    if not os.path.exists(SALES_FILE):
        print("Sales file not found.")
        return

    with open(SALES_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        sales = list(reader)

    if not sales:
        print("No sales available.")
        return

    total_sales = len(sales)
    total_revenue = sum(float(s["Total Amount"]) for s in sales)

    product_counter = Counter()

    for sale in sales:
        product_counter[sale["Product Name"]] += int(sale["Quantity Sold"])

    most_sold_product = product_counter.most_common(1)[0][0]

    print("\n" + "=" * 40)
    print("          SALES REPORT")
    print("=" * 40)
    print(f"Total Sales        : {total_sales}")
    print(f"Revenue Generated  : ₹{total_revenue:.2f}")
    print(f"Most Sold Product  : {most_sold_product}")
    print("=" * 40)