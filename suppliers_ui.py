import customtkinter as ctk
from tkinter import messagebox, ttk
from suppliers import SupplierManager
from theme import setup_theme

class SupplierGUI:
    def __init__(self, root):
        self.root = root
        self.sm = SupplierManager()
        self.theme = setup_theme()
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("Pharmacy Management System - Supplier Module")
        self.root.geometry("1000x700")
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Supplier Management",
            font=self.theme["font_title"]
        )
        self.title_label.pack(pady=20)
        
        # Tab view
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create tabs
        self.tabview.add("Add Supplier")
        self.tabview.add("Update Supplier")
        self.tabview.add("View Suppliers")
        self.tabview.add("Supplier Inventory")
        
        # Setup each tab
        self.setup_add_tab()
        self.setup_update_tab()
        self.setup_view_tab()
        self.setup_inventory_tab()
        
    def setup_add_tab(self):
        tab = self.tabview.tab("Add Supplier")
        
        # Form frame
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(pady=20, padx=20, fill="both")
        
        # Form title
        ctk.CTkLabel(
            form_frame,
            text="Add New Supplier",
            font=self.theme["font_subtitle"]
        ).pack(pady=10)
        
        # Form fields
        fields = [
            ("Name", "name_entry"),
            ("Phone", "phone_entry"),
            ("Email", "email_entry"),
            ("Address", "address_entry")
        ]
        
        self.entries = {}
        for label, name in fields:
            frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(frame, text=f"{label}:", width=100).pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            self.entries[name] = entry
        
        # Submit button
        submit_btn = ctk.CTkButton(
            form_frame,
            text="Add Supplier",
            command=self.add_supplier,
            fg_color=self.theme["primary_color"]
        )
        submit_btn.pack(pady=20)
    
    def setup_update_tab(self):
        tab = self.tabview.tab("Update Supplier")
        
        # Search frame
        search_frame = ctk.CTkFrame(tab)
        search_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            search_frame,
            text="Search Supplier to Update:",
            font=self.theme["font_subtitle"]
        ).pack(pady=5)
        
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter ID or Email")
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            command=lambda: self.search_supplier_to_update(search_entry.get()),
            width=100
        )
        search_btn.pack(side="left", padx=5)
        
        # Form frame (initially hidden)
        self.update_form_frame = ctk.CTkFrame(tab)
        
        # Form fields
        update_fields = [
            ("Name", "update_name_entry"),
            ("Phone", "update_phone_entry"),
            ("Email", "update_email_entry"),
            ("Address", "update_address_entry")
        ]
        
        self.update_entries = {}
        for label, name in update_fields:
            frame = ctk.CTkFrame(self.update_form_frame, fg_color="transparent")
            frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(frame, text=f"{label}:", width=100).pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            self.update_entries[name] = entry
        
        # Current values label
        self.current_values_label = ctk.CTkLabel(
            self.update_form_frame,
            text="Current values will appear here",
            font=self.theme["font_body"],
            text_color=self.theme["text_secondary"]
        )
        self.current_values_label.pack(pady=10)
        
        # Submit button
        self.update_supplier_id = None
        submit_btn = ctk.CTkButton(
            self.update_form_frame,
            text="Update Supplier",
            command=self.update_supplier,
            fg_color=self.theme["primary_color"]
        )
        submit_btn.pack(pady=20)
    
    def setup_view_tab(self):
        tab = self.tabview.tab("View Suppliers")
        
        # Search frame
        search_frame = ctk.CTkFrame(tab)
        search_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            search_frame,
            text="Search Suppliers:",
            font=self.theme["font_subtitle"]
        ).pack(pady=5)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Name, phone, or email")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_suppliers,
            width=100
        )
        search_btn.pack(side="left", padx=5)
        
        # Top suppliers button
        top_suppliers_btn = ctk.CTkButton(
            search_frame,
            text="Top Suppliers",
            command=self.show_top_suppliers,
            width=100,
            fg_color=self.theme["secondary_color"]
        )
        top_suppliers_btn.pack(side="left", padx=5)
        
        # Treeview for results
        self.tree_frame = ctk.CTkFrame(tab)
        self.tree_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Scrollbar
        tree_scroll = ctk.CTkScrollbar(self.tree_frame)
        tree_scroll.pack(side="right", fill="y")
        
        # Create treeview
        self.tree = ttk.Treeview(
            self.tree_frame,
            yscrollcommand=tree_scroll.set,
            selectmode="browse",
            columns=("ID", "Name", "Phone", "Email", "Address"),
            show="headings"
        )
        
        # Format columns
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=150)
        self.tree.column("Phone", width=120)
        self.tree.column("Email", width=200)
        self.tree.column("Address", width=250)
        
        # Create headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Address", text="Address")
        
        self.tree.pack(fill="both", expand=True)
        tree_scroll.configure(command=self.tree.yview)
        
        # Bind double click to view details
        self.tree.bind("<Double-1>", self.view_supplier_details)
    
    def setup_inventory_tab(self):
        tab = self.tabview.tab("Supplier Inventory")
        
        # Search frame
        search_frame = ctk.CTkFrame(tab)
        search_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            search_frame,
            text="Supplier ID:",
            font=self.theme["font_subtitle"]
        ).pack(side="left", padx=5)
        
        self.supplier_id_entry = ctk.CTkEntry(search_frame, width=100)
        self.supplier_id_entry.pack(side="left", padx=5)
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="View Inventory",
            command=self.view_supplier_inventory,
            width=150
        )
        search_btn.pack(side="left", padx=5)
        
        # Treeview for inventory
        self.inventory_tree_frame = ctk.CTkFrame(tab)
        self.inventory_tree_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Scrollbar
        inv_tree_scroll = ctk.CTkScrollbar(self.inventory_tree_frame)
        inv_tree_scroll.pack(side="right", fill="y")
        
        # Create inventory treeview
        self.inventory_tree = ttk.Treeview(
            self.inventory_tree_frame,
            yscrollcommand=inv_tree_scroll.set,
            selectmode="browse",
            columns=("Medicine", "Batch", "Quantity", "Expiry", "Days Left", "Location"),
            show="headings"
        )
        
        # Format columns
        self.inventory_tree.column("Medicine", width=150)
        self.inventory_tree.column("Batch", width=100)
        self.inventory_tree.column("Quantity", width=80, anchor="center")
        self.inventory_tree.column("Expiry", width=100)
        self.inventory_tree.column("Days Left", width=80, anchor="center")
        self.inventory_tree.column("Location", width=100)
        
        # Create headings
        self.inventory_tree.heading("Medicine", text="Medicine")
        self.inventory_tree.heading("Batch", text="Batch No.")
        self.inventory_tree.heading("Quantity", text="Qty")
        self.inventory_tree.heading("Expiry", text="Expiry Date")
        self.inventory_tree.heading("Days Left", text="Days Left")
        self.inventory_tree.heading("Location", text="Location")
        
        self.inventory_tree.pack(fill="both", expand=True)
        inv_tree_scroll.configure(command=self.inventory_tree.yview)
    
    # ====== Business Logic Methods ======
    
    def add_supplier(self):
        name = self.entries["name_entry"].get()
        phone = self.entries["phone_entry"].get()
        email = self.entries["email_entry"].get()
        address = self.entries["address_entry"].get()
        
        if not all([name, phone, email, address]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        result = self.sm.add_supplier(name, phone, email, address)
        if result["success"]:
            messagebox.showinfo("Success", result["message"])
            # Clear form
            for entry in self.entries.values():
                entry.delete(0, "end")
        else:
            messagebox.showerror("Error", result["message"])
    
    def search_supplier_to_update(self, identifier):
        if not identifier:
            messagebox.showerror("Error", "Please enter an ID or email")
            return
        
        result = self.sm.get_supplier_by_id_or_email(identifier)
        if not result["success"]:
            messagebox.showerror("Error", result["message"])
            return
        
        supplier = result["supplier"]
        self.update_supplier_id = supplier["supplier_id"]
        
        # Update current values label
        current_values = "\n".join([
            f"Name: {supplier['name']}",
            f"Phone: {supplier['phone']}",
            f"Email: {supplier['email']}",
            f"Address: {supplier['address']}"
        ])
        self.current_values_label.configure(text=current_values)
        
        # Clear and set placeholders
        for name, entry in self.update_entries.items():
            entry.delete(0, "end")
            entry.configure(placeholder_text="Leave blank to keep current")
        
        # Show form
        self.update_form_frame.pack(pady=20, padx=20, fill="both")
    
    def update_supplier(self):
        if not self.update_supplier_id:
            messagebox.showerror("Error", "No supplier selected for update")
            return
        
        name = self.update_entries["update_name_entry"].get() or None
        phone = self.update_entries["update_phone_entry"].get() or None
        email = self.update_entries["update_email_entry"].get() or None
        address = self.update_entries["update_address_entry"].get() or None
        
        # At least one field should be provided
        if all(value is None for value in [name, phone, email, address]):
            messagebox.showerror("Error", "No fields to update")
            return
        
        result = self.sm.update_supplier(
            self.update_supplier_id,
            name,
            phone,
            email,
            address
        )
        
        if result["success"]:
            messagebox.showinfo("Success", result["message"])
            # Refresh the current values
            self.search_supplier_to_update(str(self.update_supplier_id))
        else:
            messagebox.showerror("Error", result["message"])
    
    def search_suppliers(self):
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showerror("Error", "Please enter a search term")
            return
        
        results = self.sm.search_suppliers(search_term)
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if isinstance(results, list):
            for supplier in results:
                self.tree.insert("", "end", values=(
                    supplier["supplier_id"],
                    supplier["name"],
                    supplier["phone"],
                    supplier["email"],
                    supplier["address"]
                ))
        else:
            messagebox.showerror("Error", results.get("error", "Error searching suppliers"))
    
    def show_top_suppliers(self):
        results = self.sm.get_top_suppliers(5)
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if isinstance(results, list):
            for supplier in results:
                self.tree.insert("", "end", values=(
                    supplier["supplier_id"],
                    supplier["name"],
                    "",  # No phone in top suppliers
                    "",  # No email in top suppliers
                    f"Items: {supplier['total_quantity']}"
                ))
        else:
            messagebox.showerror("Error", results.get("error", "Error fetching top suppliers"))
    
    def view_supplier_details(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        item = self.tree.item(selected_item)
        supplier_id = item["values"][0]
        
        result = self.sm.get_supplier_by_id_or_email(supplier_id)
        if result["success"]:
            supplier = result["supplier"]
            details = "\n".join([f"{k}: {v}" for k, v in supplier.items()])
            messagebox.showinfo("Supplier Details", details)
        else:
            messagebox.showerror("Error", result["message"])
    
    def view_supplier_inventory(self):
        supplier_id = self.supplier_id_entry.get()
        if not supplier_id:
            messagebox.showerror("Error", "Please enter a supplier ID")
            return
    
        try:
            supplier_id = int(supplier_id)
        except ValueError:
            messagebox.showerror("Error", "Supplier ID must be a number")
            return
    
        result = self.sm.get_supplier_inventory(supplier_id)
    
        # Clear treeview
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
    
        if result["success"]:
            if result["inventory"]:  # Check if inventory list has items
                for item in result["inventory"]:
                    self.inventory_tree.insert("", "end", values=(
                    item["medicine_name"],
                    item["batch_number"],
                    item["current_quantity"],
                    item["expiry_date"],
                    item["days_until_expiry"],
                    item["location"]
                ))
            else:
                messagebox.showinfo("Info", "This supplier has no inventory items")
        else:
            messagebox.showerror("Error", result.get("error", "Error fetching inventory"))


# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    app = SupplierGUI(root)
    root.mainloop()