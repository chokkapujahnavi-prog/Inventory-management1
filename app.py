"""
Inventory Management System - Flask Web App
InfoBharat Items - Python Development Internship

Deploy on Render with:
  Build Command: pip install -r requirements.txt
  Start Command: gunicorn app:app
"""

import os
import csv
from datetime import datetime
from collections import Counter

from flask import (
    Flask, request, redirect, url_for, render_template_string,
    flash, send_from_directory
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

PRODUCTS_FILE = os.path.join(BASE_DIR, "products.csv")
SALES_FILE = os.path.join(BASE_DIR, "sales.csv")
LOW_STOCK_THRESHOLD = 10


# ─────────────────────────────────────────────
# DATA STORAGE: CSV HELPERS
# ─────────────────────────────────────────────

def normalize_product_row(row):
    return {
        "product_id": (row.get("product_id") or row.get("Product ID") or row.get("ProductId") or "").strip(),
        "name": (row.get("name") or row.get("Product Name") or row.get("ProductName") or "").strip(),
        "category": (row.get("category") or row.get("Category") or "").strip(),
        "price": row.get("price") or row.get("Price") or "0",
        "quantity": row.get("quantity") or row.get("Quantity") or "0",
        "supplier": (row.get("supplier") or row.get("Supplier") or "").strip(),
        "image_path": (row.get("image_path") or row.get("Image Path") or "").strip(),
    }


def load_products():
    products = []
    if not os.path.exists(PRODUCTS_FILE):
        return products
    with open(PRODUCTS_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not any(row.values()):
                continue
            product = normalize_product_row(row)
            try:
                product["price"] = float(product["price"])
            except ValueError:
                product["price"] = 0.0
            try:
                product["quantity"] = int(float(product["quantity"]))
            except ValueError:
                product["quantity"] = 0
            products.append(product)
    return products


def save_products(products):
    fieldnames = ["product_id", "name", "category", "price", "quantity",
                  "supplier", "image_path"]
    with open(PRODUCTS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in products:
            writer.writerow({field: p.get(field, "") for field in fieldnames})


def load_sales():
    sales = []
    if not os.path.exists(SALES_FILE):
        return sales
    with open(SALES_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["quantity_sold"] = int(row["quantity_sold"])
            row["total_amount"] = float(row["total_amount"])
            sales.append(row)
    return sales


def save_sales(sales):
    fieldnames = ["sale_id", "product_id", "product_name", "quantity_sold",
                  "total_amount", "date"]
    with open(SALES_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sales)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def find_product(products, product_id):
    return next((p for p in products if p["product_id"] == product_id), None)


# ─────────────────────────────────────────────
# TEMPLATE LAYOUT
# ─────────────────────────────────────────────

LAYOUT = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Inventory Management System</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container">
      <a class="navbar-brand" href="{{ url_for('index') }}">📦 InfoBharat Items</a>
      <div class="navbar-nav">
        <a class="nav-link" href="{{ url_for('products_list') }}">Products</a>
        <a class="nav-link" href="{{ url_for('add_product') }}">Add Product</a>
        <a class="nav-link" href="{{ url_for('low_stock') }}">Low Stock</a>
        <a class="nav-link" href="{{ url_for('record_sale') }}">Record Sale</a>
        <a class="nav-link" href="{{ url_for('sales_list') }}">Sales</a>
        <a class="nav-link" href="{{ url_for('reports') }}">Reports</a>
      </div>
    </div>
  </nav>
  <div class="container mb-5">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, message in messages %}
        <div class="alert alert-{{ 'danger' if category == 'error' else category }}">{{ message }}</div>
      {% endfor %}
    {% endwith %}
    {{ body|safe }}
  </div>
</body>
</html>
"""


def render(title, body):
    return render_template_string(LAYOUT, title=title, body=body)


# ─────────────────────────────────────────────
# ROUTES: DASHBOARD
# ─────────────────────────────────────────────

@app.route("/")
def index():
    products = load_products()
    sales = load_sales()
    total_stock = sum(p["quantity"] for p in products)
    low_count = len([p for p in products if p["quantity"] < LOW_STOCK_THRESHOLD])
    total_revenue = sum(s["total_amount"] for s in sales)

    body = render_template_string("""
      <h1 class="mb-4">Dashboard</h1>
      <div class="row g-3">
        <div class="col-md-3"><div class="card p-3"><h6>Total Products</h6><h3>{{ n }}</h3></div></div>
        <div class="col-md-3"><div class="card p-3"><h6>Total Stock</h6><h3>{{ stock }}</h3></div></div>
        <div class="col-md-3"><div class="card p-3"><h6>Low Stock Items</h6><h3>{{ low }}</h3></div></div>
        <div class="col-md-3"><div class="card p-3"><h6>Total Revenue</h6><h3>₹{{ '%.2f'|format(rev) }}</h3></div></div>
      </div>
    """, n=len(products), stock=total_stock, low=low_count, rev=total_revenue)
    return render("Dashboard", body)


# ─────────────────────────────────────────────
# ROUTES: PRODUCTS
# ─────────────────────────────────────────────

@app.route("/products")
def products_list():
    products = load_products()
    query = request.args.get("q", "").strip().lower()
    if query:
        products = [p for p in products if query in p["product_id"].lower()
                    or query in p["name"].lower()]

    body = render_template_string("""
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h1>Products</h1>
        <a href="{{ url_for('add_product') }}" class="btn btn-primary">+ Add Product</a>
      </div>
      <form class="row g-2 mb-3" method="get">
        <div class="col-auto">
          <input type="text" name="q" class="form-control" placeholder="Search by ID or name" value="{{ q }}">
        </div>
        <div class="col-auto"><button class="btn btn-outline-secondary">Search</button></div>
      </form>
      <table class="table table-bordered bg-white">
        <thead><tr>
          <th>Image</th><th>ID</th><th>Name</th><th>Category</th>
          <th>Price</th><th>Qty</th><th>Supplier</th><th></th>
        </tr></thead>
        <tbody>
        {% for p in products %}
          <tr>
            <td style="width:70px;">
              {% if p.image_path %}
                <img src="/{{ p.image_path }}" style="width:50px;height:50px;object-fit:cover;">
              {% else %}
                <span class="text-muted">—</span>
              {% endif %}
            </td>
            <td>{{ p.product_id }}</td>
            <td>{{ p.name }}</td>
            <td>{{ p.category }}</td>
            <td>₹{{ '%.2f'|format(p.price) }}</td>
            <td>{{ p.quantity }}{% if p.quantity < 10 %} ⚠️{% endif %}</td>
            <td>{{ p.supplier }}</td>
            <td class="text-nowrap">
              <a href="{{ url_for('edit_product', product_id=p.product_id) }}" class="btn btn-sm btn-outline-secondary">Edit</a>
              <form method="post" action="{{ url_for('delete_product', product_id=p.product_id) }}" style="display:inline;" onsubmit="return confirm('Delete this product?');">
                <button class="btn btn-sm btn-outline-danger">Delete</button>
              </form>
            </td>
          </tr>
        {% else %}
          <tr><td colspan="8" class="text-center text-muted">No products found.</td></tr>
        {% endfor %}
        </tbody>
      </table>
    """, products=products, q=query)
    return render("Products", body)


PRODUCT_FORM = """
  <h1 class="mb-4">{{ heading }}</h1>
  <form method="post" enctype="multipart/form-data" class="bg-white p-4 border rounded">
    <div class="mb-3">
      <label class="form-label">Product ID</label>
      <input type="text" name="product_id" class="form-control" value="{{ p.product_id if p else '' }}" {% if p %}readonly{% endif %} required>
    </div>
    <div class="mb-3">
      <label class="form-label">Name</label>
      <input type="text" name="name" class="form-control" value="{{ p.name if p else '' }}" required>
    </div>
    <div class="mb-3">
      <label class="form-label">Category</label>
      <input type="text" name="category" class="form-control" value="{{ p.category if p else '' }}">
    </div>
    <div class="mb-3">
      <label class="form-label">Price</label>
      <input type="number" step="0.01" min="0" name="price" class="form-control" value="{{ p.price if p else '' }}" required>
    </div>
    <div class="mb-3">
      <label class="form-label">Quantity</label>
      <input type="number" min="0" name="quantity" class="form-control" value="{{ p.quantity if p else '' }}" required>
    </div>
    <div class="mb-3">
      <label class="form-label">Supplier</label>
      <input type="text" name="supplier" class="form-control" value="{{ p.supplier if p else '' }}">
    </div>
    <div class="mb-3">
      <label class="form-label">Product Image</label>
      <input type="file" name="image" class="form-control" accept=".png,.jpg,.jpeg,.gif,.webp">
      {% if p and p.image_path %}
        <div class="mt-2"><img src="/{{ p.image_path }}" style="width:80px;"></div>
      {% endif %}
    </div>
    <button class="btn btn-primary">Save</button>
    <a href="{{ url_for('products_list') }}" class="btn btn-link">Cancel</a>
  </form>
"""


@app.route("/products/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        products = load_products()
        product_id = request.form.get("product_id", "").strip()
        name = request.form.get("name", "").strip()

        if not product_id or not name:
            flash("Product ID and Name are required.", "error")
            return redirect(url_for("add_product"))

        if find_product(products, product_id):
            flash(f"Product ID '{product_id}' already exists.", "error")
            return redirect(url_for("add_product"))

        try:
            price = float(request.form.get("price", 0))
            quantity = int(request.form.get("quantity", 0))
            if price < 0 or quantity < 0:
                raise ValueError
        except ValueError:
            flash("Price and quantity must be valid non-negative numbers.", "error")
            return redirect(url_for("add_product"))

        image_path = ""
        file = request.files.get("image")
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(f"{product_id}_{file.filename}")
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            image_path = f"static/uploads/{filename}"

        products.append({
            "product_id": product_id,
            "name": name,
            "category": request.form.get("category", "").strip(),
            "price": price,
            "quantity": quantity,
            "supplier": request.form.get("supplier", "").strip(),
            "image_path": image_path,
        })
        save_products(products)
        flash(f"Product '{name}' added successfully!", "success")
        return redirect(url_for("products_list"))

    body = render_template_string(PRODUCT_FORM, heading="Add Product", p=None)
    return render("Add Product", body)


@app.route("/products/<product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    products = load_products()
    product = find_product(products, product_id)
    if not product:
        flash(f"Product ID '{product_id}' not found.", "error")
        return redirect(url_for("products_list"))

    if request.method == "POST":
        product["name"] = request.form.get("name", "").strip() or product["name"]
        product["category"] = request.form.get("category", "").strip()
        product["supplier"] = request.form.get("supplier", "").strip()

        try:
            price = float(request.form.get("price", product["price"]))
            quantity = int(request.form.get("quantity", product["quantity"]))
            if price < 0 or quantity < 0:
                raise ValueError
            product["price"] = price
            product["quantity"] = quantity
        except ValueError:
            flash("Invalid price or quantity — kept previous values.", "error")

        file = request.files.get("image")
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(f"{product_id}_{file.filename}")
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            product["image_path"] = f"static/uploads/{filename}"

        save_products(products)
        flash("Product updated successfully!", "success")
        return redirect(url_for("products_list"))

    body = render_template_string(PRODUCT_FORM, heading="Edit Product", p=product)
    return render("Edit Product", body)


@app.route("/products/<product_id>/delete", methods=["POST"])
def delete_product(product_id):
    products = load_products()
    product = find_product(products, product_id)
    if not product:
        flash(f"Product ID '{product_id}' not found.", "error")
    else:
        products.remove(product)
        save_products(products)
        flash("Product deleted successfully!", "success")
    return redirect(url_for("products_list"))


# ─────────────────────────────────────────────
# ROUTES: STOCK
# ─────────────────────────────────────────────

@app.route("/stock/low")
def low_stock():
    products = load_products()
    low = [p for p in products if p["quantity"] < LOW_STOCK_THRESHOLD]
    body = render_template_string("""
      <h1 class="mb-4">Low Stock Alert (below {{ threshold }} units)</h1>
      <table class="table table-bordered bg-white">
        <thead><tr><th>ID</th><th>Name</th><th>Quantity</th></tr></thead>
        <tbody>
        {% for p in low %}
          <tr class="table-warning"><td>{{ p.product_id }}</td><td>{{ p.name }}</td><td>{{ p.quantity }} ⚠️</td></tr>
        {% else %}
          <tr><td colspan="3" class="text-center text-muted">All products have sufficient stock.</td></tr>
        {% endfor %}
        </tbody>
      </table>
    """, low=low, threshold=LOW_STOCK_THRESHOLD)
    return render("Low Stock", body)


# ─────────────────────────────────────────────
# ROUTES: SALES
# ─────────────────────────────────────────────

@app.route("/sales/add", methods=["GET", "POST"])
def record_sale():
    products = load_products()

    if request.method == "POST":
        sales = load_sales()
        product_id = request.form.get("product_id", "")
        product = find_product(products, product_id)

        if not product:
            flash("Product not found.", "error")
            return redirect(url_for("record_sale"))

        try:
            qty = int(request.form.get("quantity", 0))
            if qty <= 0:
                raise ValueError
        except ValueError:
            flash("Quantity must be a positive integer.", "error")
            return redirect(url_for("record_sale"))

        if qty > product["quantity"]:
            flash(f"Insufficient stock. Available: {product['quantity']}", "error")
            return redirect(url_for("record_sale"))

        total = round(qty * product["price"], 2)
        sale_id = f"SALE{len(sales) + 1:04d}"
        sales.append({
            "sale_id": sale_id,
            "product_id": product_id,
            "product_name": product["name"],
            "quantity_sold": qty,
            "total_amount": total,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        product["quantity"] -= qty
        save_products(products)
        save_sales(sales)

        msg = f"Sale recorded! {sale_id} | Total: ₹{total:.2f}"
        if product["quantity"] < LOW_STOCK_THRESHOLD:
            msg += f" — ⚠️ Stock for '{product['name']}' is now low ({product['quantity']} units)."
        flash(msg, "success")
        return redirect(url_for("sales_list"))

    body = render_template_string("""
      <h1 class="mb-4">Record Sale</h1>
      <form method="post" class="bg-white p-4 border rounded">
        <div class="mb-3">
          <label class="form-label">Product</label>
          <select name="product_id" class="form-select" required>
            {% for p in products %}
              <option value="{{ p.product_id }}">{{ p.product_id }} — {{ p.name }} (Stock: {{ p.quantity }}, ₹{{ '%.2f'|format(p.price) }})</option>
            {% endfor %}
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Quantity</label>
          <input type="number" min="1" name="quantity" class="form-control" required>
        </div>
        <button class="btn btn-primary">Record Sale</button>
      </form>
    """, products=products)
    return render("Record Sale", body)


@app.route("/sales")
def sales_list():
    sales = load_sales()
    total_qty = sum(s["quantity_sold"] for s in sales)
    total_revenue = sum(s["total_amount"] for s in sales)
    most_sold = None
    if sales:
        counter = Counter()
        for s in sales:
            counter[s["product_name"]] += s["quantity_sold"]
        most_sold = counter.most_common(1)[0]

    body = render_template_string("""
      <h1 class="mb-4">Sales</h1>
      <div class="row g-3 mb-4">
        <div class="col-md-4"><div class="card p-3"><h6>Total Sold</h6><h3>{{ qty }}</h3></div></div>
        <div class="col-md-4"><div class="card p-3"><h6>Revenue</h6><h3>₹{{ '%.2f'|format(rev) }}</h3></div></div>
        <div class="col-md-4"><div class="card p-3"><h6>Best Seller</h6><h3>{{ most[0] if most else '—' }}</h3></div></div>
      </div>
      <table class="table table-bordered bg-white">
        <thead><tr><th>Sale ID</th><th>Product</th><th>Qty</th><th>Total</th><th>Date</th></tr></thead>
        <tbody>
        {% for s in sales|reverse %}
          <tr><td>{{ s.sale_id }}</td><td>{{ s.product_name }}</td><td>{{ s.quantity_sold }}</td>
              <td>₹{{ '%.2f'|format(s.total_amount) }}</td><td>{{ s.date }}</td></tr>
        {% else %}
          <tr><td colspan="5" class="text-center text-muted">No sales recorded yet.</td></tr>
        {% endfor %}
        </tbody>
      </table>
    """, sales=sales, qty=total_qty, rev=total_revenue, most=most_sold)
    return render("Sales", body)


# ─────────────────────────────────────────────
# ROUTES: REPORTS
# ─────────────────────────────────────────────

@app.route("/reports")
def reports():
    products = load_products()
    sales = load_sales()

    categories = sorted(set(p["category"] for p in products if p["category"]))
    total_stock = sum(p["quantity"] for p in products)
    total_revenue = sum(s["total_amount"] for s in sales)

    most_sold = None
    if sales:
        counter = Counter()
        for s in sales:
            counter[s["product_name"]] += s["quantity_sold"]
        most_sold = counter.most_common(1)[0]

    body = render_template_string("""
      <h1 class="mb-4">Reports</h1>
      <div class="row g-4">
        <div class="col-md-6">
          <div class="card p-3">
            <h5>Inventory Report</h5>
            <p>Total Products: {{ n }}</p>
            <p>Total Categories: {{ categories|length }}</p>
            <p>Available Stock: {{ stock }} units</p>
            <p>Categories: {{ categories|join(', ') if categories else '—' }}</p>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card p-3">
            <h5>Sales Report</h5>
            <p>Total Transactions: {{ sales|length }}</p>
            <p>Revenue Generated: ₹{{ '%.2f'|format(rev) }}</p>
            <p>Most Sold Product: {{ most[0] ~ ' (' ~ most[1]|string ~ ' units)' if most else '—' }}</p>
          </div>
        </div>
      </div>
    """, n=len(products), categories=categories, stock=total_stock,
       sales=sales, rev=total_revenue, most=most_sold)
    return render("Reports", body)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
