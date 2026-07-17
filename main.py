from inventory import (
    add_product,
    view_products,
    search_product,
    update_product,
    delete_product,
    add_stock,
    low_stock_alert
)

from sales import (
    record_sale,
    sales_summary
)

from reports import (
    inventory_report,
    sales_report
)


def menu():
    while True:
        print("\n" + "=" * 50)
        print("     INVENTORY MANAGEMENT SYSTEM")
        print("=" * 50)
        print("1. Add Product")
        print("2. View Products")
        print("3. Search Product")
        print("4. Update Product")
        print("5. Delete Product")
        print("6. Add Stock")
        print("7. Low Stock Alert")
        print("8. Record Sale")
        print("9. Sales Summary")
        print("10. Inventory Report")
        print("11. Sales Report")
        print("12. Exit")
        print("=" * 50)

        choice = input("Enter your choice: ")

        if choice == "1":
            add_product()

        elif choice == "2":
            view_products()

        elif choice == "3":
            search_product()

        elif choice == "4":
            update_product()

        elif choice == "5":
            delete_product()

        elif choice == "6":
            add_stock()

        elif choice == "7":
            low_stock_alert()

        elif choice == "8":
            record_sale()

        elif choice == "9":
            sales_summary()

        elif choice == "10":
            inventory_report()

        elif choice == "11":
            sales_report()

        elif choice == "12":
            print("\nThank you for using Inventory Management System.")
            break

        else:
            print("\nInvalid choice! Please try again.")


if __name__ == "__main__":
    menu()