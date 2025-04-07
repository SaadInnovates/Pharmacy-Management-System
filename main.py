from inventory import PharmacyInventory
from medicines import Medicine
from prescriptions import PrescriptionManager
from suppliers import SupplierManager
from users import UserManager
import getpass
import re
from datetime import datetime
from predictor import MedicineEffectivenessPredictor

def display_title():
    print("\n" + "="*50)
    print("PHARMACY MANAGEMENT SYSTEM".center(50))
    print("="*50)

def login_screen(user_manager):
    """Handle user login with role-based access"""
    while True:
        display_title()
        print("\nPlease login to continue")
        email = input("Email: ")
        
        try:
            password = getpass.getpass("Password: ")
        except Exception as e:
            print(f"\nWarning: Could not hide password input ({str(e)}). "
                  "Password will be visible.")
            password = input("Password (visible): ")
        
        result = user_manager.authenticate_user(email, password)
        if result["success"]:
            return result["user"]
        else:
            print(f"\nError: {result['message']}")
            if input("\nTry again? (y/n): ").lower() != 'y':
                return None

def main_menu(user_role):
    """Show appropriate menu based on user role"""
    print("\n" + "="*50)
    print(f"MAIN MENU ({user_role})".center(50))
    print("="*50)
    
    print("\n1. Inventory Management")
    print("2. Medicine Management")
    print("3. Prescription Management")
    print("4. Supplier Management")
    if user_role == "Admin":
        print("5. User Management")
        print("6. Medicine Effectiveness Prediction")
    print("0. Exit")
    
    return input("\nSelect an option: ")

def inventory_menu():
    print("\n" + "-"*50)
    print("INVENTORY MANAGEMENT".center(50))
    print("-"*50)
    print("\n1. Add Inventory Item")
    print("2. Update Inventory Quantity")
    print("3. View Low Stock Items")
    print("4. View Expiring Soon")
    print("5. Transfer Inventory")
    print("6. Generate Inventory Report")
    print("0. Return to Main Menu")
    return input("\nSelect an option: ")

def medicine_menu():
    print("\n" + "-"*50)
    print("MEDICINE MANAGEMENT".center(50))
    print("-"*50)
    print("\n1. Add New Medicine")
    print("2. Update Medicine Details")
    print("3. Delete Medicine")
    print("4. View All Medicines")
    print("5. Search Medicines")
    print("6. View Expired Medicines")
    print("7. View Low Stock Medicines")
    print("8. View Nearly Expiring Medicines")
    print("0. Return to Main Menu")
    return input("\nSelect an option: ")

def prescription_menu():
    print("\n" + "-"*50)
    print("PRESCRIPTION MANAGEMENT".center(50))
    print("-"*50)
    print("\n1. Create Prescription")
    print("2. View Prescription")
    print("3. Update Prescription")
    print("4. Delete Prescription")
    print("5. View Prescriptions by Date")
    print("6. View Prescriptions by Amount Range")
    print("0. Return to Main Menu")
    return input("\nSelect an option: ")

def supplier_menu():
    print("\n" + "-"*50)
    print("SUPPLIER MANAGEMENT".center(50))
    print("-"*50)
    print("\n1. Add New Supplier")
    print("2. Update Supplier")
    print("3. View Supplier Details")
    print("4. Search Suppliers")
    print("5. View Supplier Inventory")
    print("6. View Top Suppliers")
    print("0. Return to Main Menu")
    return input("\nSelect an option: ")

def user_menu():
    print("\n" + "-"*50)
    print("USER MANAGEMENT".center(50))
    print("-"*50)
    print("\n1. Register New User")
    print("2. Update User")
    print("3. View User Details")
    print("4. List All Users")
    print("5. Reset Password")
    print("6. Delete User")
    print("0. Return to Main Menu")
    return input("\nSelect an option: ")

def handle_inventory():
    inventory = PharmacyInventory()
    while True:
        choice = inventory_menu()
        
        if choice == '1':  # Add Inventory Item
            print("\nAdd New Inventory Item")
            try:
                medicine_name = input("Medicine Name: ")
                supplier_id = int(input("Supplier ID: "))
                quantity = int(input("Quantity Added: "))
                batch = input("Batch Number: ")
                expiry = input("Expiry Date (YYYY-MM-DD): ")
                location = input("Location: ")
                medicine_id=Medicine.get_id_by_name(medicine_name)
                
                result = inventory.add_inventory_item(medicine_id, supplier_id, quantity, batch, expiry, location)
                print(result["message"])
            except ValueError:
                print("Invalid input. Please enter valid numbers for IDs and quantity.")
                
        elif choice == '2':  # Update Inventory Quantity
            try:
                inv_id = int(input("Inventory ID: "))
                new_qty = int(input("New Quantity: "))
                result = inventory.update_inventory_quantity(inv_id, new_qty)
                print(result["message"])
            except ValueError:
                print("Invalid input. Please enter valid numbers.")
                
        elif choice == '3':  # View Low Stock
            threshold = input("Enter threshold (default 10): ")
            threshold = int(threshold) if threshold.isdigit() else 10
            items = inventory.get_low_stock_items(threshold)
            if isinstance(items, list):
                print("\nLow Stock Items:")
                print("-" * 60)
                print(f"{'ID':<8}{'Medicine':<20}{'Quantity':<12}{'Location':<20}")
                print("-" * 60)
                for item in items:
                    print(f"{item['inventory_id']:<8}{item['medicine_name']:<20}{item['current_quantity']:<12}{item['location']:<20}")
            else:
                print(items.get("error", "Error fetching low stock items"))
                
        elif choice == '4':  # View Expiring Soon
            days = input("Enter days threshold (default 30): ")
            days = int(days) if days.isdigit() else 30
            items = inventory.get_expiring_soon(days)
            if isinstance(items, list):
                print("\nItems Expiring Soon:")
                print("-" * 80)
                print(f"{'ID':<8}{'Medicine':<20}{'Quantity':<12}{'Expiry Date':<15}{'Days Left':<12}{'Location':<15}")
                print("-" * 80)
                for item in items:
                    print(f"{item['inventory_id']:<8}{item['medicine_name']:<20}{item['current_quantity']:<12}"
                          f"{item['expiry_date'].strftime('%Y-%m-%d') if item['expiry_date'] else 'N/A':<15}"
                          f"{item['days_until_expiry']:<12}{item['location']:<15}")
            else:
                print(items.get("error", "Error fetching expiring items"))
                
        elif choice == '5':  # Transfer Inventory
            try:
                inv_id = int(input("Inventory ID to transfer: "))
                quantity = int(input("Quantity to transfer: "))
                location = input("New location: ")
                result = inventory.transfer_inventory(inv_id, location, quantity)
                print(result["message"])
            except ValueError:
                print("Invalid input. Please enter valid numbers.")
                
        elif choice == '6':  # Generate Report
            report = inventory.generate_inventory_report()
            if "report" in report:
                print("\nInventory Report Summary:")
                print("-" * 80)
                print(f"{'Medicine':<25}{'Total Qty':<12}{'Batches':<10}{'Earliest Expiry':<20}{'Locations':<20}")
                print("-" * 80)
                for item in report["report"]:
                    print(f"{item['medicine_name']:<25}{item['total_quantity']:<12}{item['batch_count']:<10}"
                          f"{item['earliest_expiry'].strftime('%Y-%m-%d') if item['earliest_expiry'] else 'N/A':<20}"
                          f"{item['locations']:<20}")
                print("-" * 80)
                print(f"\nSummary Statistics:")
                print(f"Total Items: {report['summary']['total_items']}")
                print(f"Unique Medicines: {report['summary']['unique_medicines']}")
                print(f"Items Expiring Soon (≤30 days): {report['summary']['items_expiring_soon']}")
            else:
                print(report.get("error", "Error generating report"))
                
        elif choice == '7':  # Search Inventory
            search_term = input("Enter search term (medicine name, batch, or location): ")
            results = inventory.search_inventory(search_term)
            if isinstance(results, list):
                print("\nSearch Results:")
                print("-" * 80)
                print(f"{'ID':<8}{'Medicine':<20}{'Batch':<15}{'Qty':<8}{'Expiry':<12}{'Location':<15}")
                print("-" * 80)
                for item in results:
                    print(f"{item['inventory_id']:<8}{item['medicine_name']:<20}{item['batch_number']:<15}"
                          f"{item['current_quantity']:<8}{item['expiry_date'].strftime('%Y-%m-%d') if item['expiry_date'] else 'N/A':<12}"
                          f"{item['location']:<15}")
            else:
                print(results.get("message", "No results found"))
                
        elif choice == '0':
            break
            
        else:
            print("Invalid choice, please try again")
        
        input("\nPress Enter to continue...")

def handle_medicines():
    while True:
        choice = medicine_menu()
        
        if choice == '1':  # Add Medicine
            print("\nAdd New Medicine")
            name = input("Name: ")
            manufacturer = input("Manufacturer: ")
            try:
                price = float(input("Price: "))
                category = input("Category: ")
                description = input("Description (optional): ") or None
                dosage = input("Dosage (optional): ") or None
                rx = input("Requires prescription? (y/n): ").lower() == 'y'
                
                med = Medicine(name, manufacturer, price, category, description, dosage, rx)
                med.add_in_db()
            except ValueError:
                print("Invalid price. Please enter a valid number.")
                
        elif choice == '2':  # Update Medicine
            name = input("Enter medicine name to update: ")
            try:
                new_price = input("New price (leave blank to keep current): ")
                new_price = float(new_price) if new_price else None
                new_category = input("New category (leave blank to keep current): ") or None
                new_desc = input("New description (leave blank to keep current): ") or None
                new_dosage = input("New dosage (leave blank to keep current): ") or None
                new_rx = input("Change prescription requirement? (y/n/leave blank): ").lower()
                new_rx = True if new_rx == 'y' else False if new_rx == 'n' else None
                
                med = Medicine(name, "", 0, "")  # Temporary object
                med.update_medicine(new_price, new_category, new_desc, new_dosage, new_rx)
            except ValueError:
                print("Invalid price. Please enter a valid number.")
                
        elif choice == '3':  # Delete Medicine
            name = input("Enter medicine name to delete: ")
            med = Medicine(name, "", 0, "")
            med.delete_medicine()
            
        elif choice == '4':  # View All
            Medicine.read_all_medicines()
            
        elif choice == '5':  # Search
            term = input("Enter search term: ")
            Medicine.search_medicines(term)
            
        elif choice == '6':  # Expired
            Medicine.get_expired_medicines()
            
        elif choice == '7':  # Low Stock
            threshold = input("Enter threshold (default 10): ")
            threshold = int(threshold) if threshold.isdigit() else 10
            Medicine.get_low_stock_medicines(threshold)
            
        elif choice == '8':  # Nearly Expiring
            days = input("Enter days threshold (default 30): ")
            days = int(days) if days.isdigit() else 30
            Medicine.get_nearly_expiring_medicines(days)
            
        elif choice == '0':
            break
            
        else:
            print("Invalid choice, please try again")
        
        input("\nPress Enter to continue...")

def handle_prescriptions():
    pm = PrescriptionManager()
    while True:
        choice = prescription_menu()
        
        if choice == '1':  # Create
            pm.create_prescription()
            
        elif choice == '2':  # View
            try:
                pres_id = int(input("Enter prescription ID: "))
                pm.read_prescription(pres_id)
            except ValueError:
                print("Invalid ID. Please enter a number.")
                
        elif choice == '3':  # Update
            try:
                pres_id = int(input("Enter prescription ID: "))
                pm.update_prescription(pres_id)
            except ValueError:
                print("Invalid ID. Please enter a number.")
                
        elif choice == '4':  # Delete
            try:
                pres_id = int(input("Enter prescription ID: "))
                pm.delete_prescription(pres_id)
            except ValueError:
                print("Invalid ID. Please enter a number.")
                
        elif choice == '5':  # By Date
            date_str = input("Enter date (YYYY-MM-DD): ")
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                pm.get_prescriptions_by_date(date_obj)
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                
        elif choice == '6':  # By Amount
            try:
                min_amt = float(input("Minimum amount: "))
                max_amt = float(input("Maximum amount: "))
                pm.get_prescriptions_by_amount_range(min_amt, max_amt)
            except ValueError:
                print("Invalid amount. Please enter numbers.")
                
        elif choice == '0':
            break
            
        else:
            print("Invalid choice, please try again")
        
        input("\nPress Enter to continue...")

def handle_suppliers():
    sm = SupplierManager()
    while True:
        choice = supplier_menu()
        
        if choice == '1':  # Add
            print("\nAdd New Supplier")
            name = input("Name: ")
            phone = input("Phone: ")
            email = input("Email: ")
            address = input("Address: ")
            
            result = sm.add_supplier(name, phone, email, address)
            print(result["message"])
            
        elif choice == '2':  # Update
            try:
                supp_id = int(input("Supplier ID: "))
                supplier=sm.get_supplier_by_id_or_email(supp_id)
                if not supplier.get("success"):
                    print(f"\nError: {supplier.get('message', 'No supplier exists with this ID!')}")
                else:
                    print("Leave fields blank to keep current values")
                    name = input("New Name: ") or None
                    phone = input("New Phone: ") or None
                    email = input("New Email: ") or None
                    address = input("New Address: ") or None
                
                    result = sm.update_supplier(supp_id, name, phone, email, address)
                    print(result["message"])
            except ValueError:
                print("Invalid ID. Please enter a number.")
                
        elif choice == '3':  # View
            try:
                supp_id = int(input("Supplier ID: "))
                result = sm.get_supplier_by_id_or_email(supp_id)
                if result["success"]:
                    print("\nSupplier Details:")
                    for k, v in result["supplier"].items():
                        print(f"{k}: {v}")
                else:
                    print(result["message"])
            except ValueError:
                print("Invalid ID. Please enter a number.")
                
        elif choice == '4':  # Search
            term = input("Search term: ")
            results = sm.search_suppliers(term)
            if isinstance(results, list):
                print("\nSearch Results:")
                for supp in results:
                    print(f"{supp['supplier_id']}: {supp['name']} - {supp['phone']}")
            else:
                print(results.get("error", "Error searching"))
                
        elif choice == '5':  # Inventory
            try:
                supp_id = int(input("Supplier ID: "))
                supplier=sm.get_supplier_by_id_or_email(supp_id)
                if not supplier.get("success"):
                    print(f"\nError: {supplier.get('message', 'No supplier exists with this ID!')}")
                else:
                    result = sm.get_supplier_inventory(supp_id)
                    if "inventory" in result:
                        print(f"\nInventory from Supplier {supp_id}:")
                        for item in result["inventory"]:
                            print(f"{item['medicine_name']}: {item['current_quantity']} (Expires in {item['days_until_expiry']} days)")
                    else:
                        print(result.get("error", "No Inventory by this supplier."))
            except ValueError:
                print("Invalid ID. Please enter a number.")

        
                
        elif choice == '6':  # Top Suppliers
            try:
                limit = int(input("Number of suppliers to show (default 5): ") or 5)
                results = sm.get_top_suppliers(limit)
                if isinstance(results, list):
                    print("\nTop Suppliers by Inventory Volume:")
                    for supp in results:
                        print(f"{supp['name']}: {supp['total_quantity']} items")
                else:
                    print(results.get("error", "Error fetching top suppliers"))
            except ValueError:
                print("Invalid number. Using default 5.")
                results = sm.get_top_suppliers(5)
                if isinstance(results, list):
                    print("\nTop Suppliers by Inventory Volume:")
                    for supp in results:
                        print(f"{supp['name']}: {supp['total_quantity']} items")
                else:
                    print(results.get("error", "Error fetching top suppliers"))
                    
        elif choice == '0':
            break
            
        else:
            print("Invalid choice, please try again")
        
        input("\nPress Enter to continue...")

def handle_users(user_manager, current_user_role,current_user):
    while True:
        choice = user_menu()
        
        if choice == '1':  # Register
            if current_user_role != "Admin":
                print("Only Admins can register new users!")
                continue
                
            print("\nRegister New User")
            name = input("Full Name: ")
            email = input("Email: ")
            phone = input("Phone: ")
            role = input("Role (Admin/Pharmacist): ").capitalize()
            if role not in ["Admin", "Pharmacist"]:
                print("Invalid role. Must be Admin or Pharmacist")
                continue
            password = getpass.getpass("Password: ")
            confirm = getpass.getpass("Confirm Password: ")
            
            if password != confirm:
                print("Passwords don't match!")
                continue
                
            result = user_manager.register_user(name, email, phone, role, password)
            print(result["message"])
            
        elif choice == '2':  # Update
            try:
                user_id = int(input("User ID to update: "))
                print("Leave fields blank to keep current values")
                name = input("New Name: ") or None
                email = input("New Email: ") or None
                phone = input("New Phone: ") or None
                role = input("New Role (Admin/Pharmacist): ").capitalize() or None
                if role and role not in ["Admin", "Pharmacist"]:
                    print("Invalid role. Must be Admin or Pharmacist")
                    continue
                    
                # Only allow password change if admin or updating own account
                change_pass = False
                if current_user_role == "Admin" or user_id == current_user.get("user_id"):
                    if input("Change password? (y/n): ").lower() == 'y':
                        new_pass = getpass.getpass("New Password: ")
                        confirm = getpass.getpass("Confirm Password: ")
                        if new_pass == confirm:
                            password = new_pass
                            change_pass = True
                        else:
                            print("Passwords don't match!")
                            continue
                
                result = user_manager.update_user(
                    user_id, name, email, phone, role, 
                    password if change_pass else None
                )
                print(result["message"])
            except ValueError:
                print("Invalid ID. Please enter a number.")
                
        elif choice == '3':  # View
            try:
                user_id = int(input("User ID: "))
                result = user_manager.get_user_by_id(user_id)
                if result["success"]:
                    print("\nUser Details:")
                    for k, v in result["user"].items():
                        print(f"{k}: {v}")
                else:
                    print(result["message"])
            except ValueError:
                print("Invalid ID. Please enter a number.")
                
        elif choice == '4':  # List All
            if current_user_role != "Admin":
                print("Only Admins can view all users!")
                continue
                
            role_filter = None
            if input("Filter by role? (y/n): ").lower() == 'y':
                role = input("Role (Admin/Pharmacist): ").capitalize()
                if role in ["Admin", "Pharmacist"]:
                    role_filter = role
                    
            users = user_manager.get_all_users(role_filter)
            if isinstance(users, list):
                print("\nAll Users:")
                for user in users:
                    print(f"{user['user_id']}: {user['name']} ({user['role']})")
            else:
                print(users.get("error", "Error fetching users"))
                
        elif choice == '5':  # Reset Password
            if current_user_role != "Admin":
                print("Only Admins can reset passwords!")
                continue
                
            email = input("User Email: ")
            new_pass = getpass.getpass("New Password: ")
            confirm = getpass.getpass("Confirm Password: ")
            
            if new_pass != confirm:
                print("Passwords don't match!")
                continue
                
            result = user_manager.reset_password(email, new_pass)
            print(result["message"])
            
        elif choice == '6':  # Delete
            if current_user_role != "Admin":
                print("Only Admins can delete users!")
                continue
                
            try:
                user_id = int(input("User ID to delete: "))
                result = user_manager.delete_user(user_id)
                print(result["message"])
            except ValueError:
                print("Invalid ID. Please enter a number.")
                
        elif choice == '0':
            break
            
        else:
            print("Invalid choice, please try again")
        
        input("\nPress Enter to continue...")

def main():
    user_manager = UserManager()
    current_user = login_screen(user_manager)
    
    if not current_user:
        print("\nGoodbye!")
        return
        
    while True:
        choice = main_menu(current_user["role"])
        
        if choice == '1':  # Inventory
            handle_inventory()
        elif choice == '2':  # Medicines
            handle_medicines()
        elif choice == '3':  # Prescriptions
            handle_prescriptions()
        elif choice == '4':  # Suppliers
            handle_suppliers()
        elif choice == '5' and current_user["role"] == "Admin":  # Users
            handle_users(user_manager, current_user["role"],current_user)
        elif choice == '6':
            medicine_name = input("Enter medicine name: ")
            condition = input("Enter condition (e.g., fever, infection, headache): ")
            medicine_predictor=MedicineEffectivenessPredictor()
            effectiveness = medicine_predictor.predict_effectiveness(medicine_name, condition)
            print(f"\nEstimated Effectiveness: {round(effectiveness * 100, 2)}%")
            input("\nPress Enter to continue...")

        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice, please try again")

if __name__ == "__main__":
    main()