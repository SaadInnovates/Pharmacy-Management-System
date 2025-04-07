# medicines_gui.py
import customtkinter
from tkinter import messagebox, ttk
from theme import setup_theme
from medicines import Medicine
from datetime import datetime


def validate_price(value):
            try:
                price = float(value)
                if price <= 0:
                    return False
                return True
            except ValueError:
                return False
            
# Set custom font styles
LARGE_FONT = ("Arial", 14)
MEDIUM_FONT = ("Arial", 12)
SMALL_FONT = ("Arial", 10)

class MedicinesWindow:
    def __init__(self):
        self.theme = setup_theme()
        self.window = customtkinter.CTk()
        self.window.title("Pharmacy Management System - Medicines")
        self.window.geometry("1400x900")
        
        # Configure grid layout
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        self.create_widgets()
        self.load_medicines_list()
        
    def create_widgets(self):
        # Main frame with padding
        main_frame = customtkinter.CTkFrame(
            self.window, 
            fg_color=self.theme["bg_color"],
            corner_radius=10
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title frame with accent color
        title_frame = customtkinter.CTkFrame(
            main_frame, 
            fg_color=self.theme["primary_color"],
            corner_radius=8,
            height=50
        )
        title_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = customtkinter.CTkLabel(
            title_frame,
            text="MEDICINE MANAGEMENT",
            font=("Arial", 18, "bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=20)
        
        # Action buttons frame with improved layout
        action_frame = customtkinter.CTkFrame(
            main_frame, 
            fg_color="transparent",
            height=50
        )
        action_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Action buttons with consistent styling
        button_style = {
            "width": 140,
            "height": 40,
            "font": ("Arial", 12, "bold"),
            "corner_radius": 8
        }
        
        add_button = customtkinter.CTkButton(
            action_frame,
            text="➕ Add Medicine",
            fg_color="#28a745",
            hover_color="#218838",
            command=self.show_add_dialog,
            **button_style
        )
        add_button.pack(side="left", padx=5)
        
        update_button = customtkinter.CTkButton(
            action_frame,
            text="✏️ Update Medicine",
            fg_color="#17a2b8",
            hover_color="#138496",
            command=self.show_update_dialog,
            **button_style
        )
        update_button.pack(side="left", padx=5)
        
        delete_button = customtkinter.CTkButton(
            action_frame,
            text="🗑️ Delete Medicine",
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self.delete_medicine,
            **button_style
        )
        delete_button.pack(side="left", padx=5)
        
        # Reports frame with improved layout
        reports_frame = customtkinter.CTkFrame(
            main_frame, 
            fg_color="transparent"
        )
        reports_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        report_button_style = {
            "width": 180,
            "height": 35,
            "font": ("Arial", 11),
            "corner_radius": 6
        }
        
        expired_button = customtkinter.CTkButton(
            reports_frame,
            text="⚠️ Expired Medicines",
            fg_color="#ffc107",
            hover_color="#e0a800",
            text_color="black",
            command=self.show_expired_medicines,
            **report_button_style
        )
        expired_button.pack(side="left", padx=5)
        
        low_stock_button = customtkinter.CTkButton(
            reports_frame,
            text="📉 Low Stock",
            fg_color="#fd7e14",
            hover_color="#e36209",
            command=self.show_low_stock_dialog,
            **report_button_style
        )
        low_stock_button.pack(side="left", padx=5)
        
        nearly_expiring_button = customtkinter.CTkButton(
            reports_frame,
            text="⏳ Nearly Expiring",
            fg_color="#6f42c1",
            hover_color="#5a3d8e",
            command=self.show_nearly_expiring_dialog,
            **report_button_style
        )
        nearly_expiring_button.pack(side="left", padx=5)
        
        # Search frame with improved styling
        search_frame = customtkinter.CTkFrame(
            main_frame, 
            fg_color="transparent"
        )
        search_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        self.search_entry = customtkinter.CTkEntry(
            search_frame,
            placeholder_text="Search medicines by name, manufacturer or category...",
            width=400,
            height=40,
            font=MEDIUM_FONT,
            corner_radius=8
        )
        self.search_entry.pack(side="left", padx=5)
        
        search_button = customtkinter.CTkButton(
            search_frame,
            text="🔍 Search",
            width=100,
            height=40,
            font=MEDIUM_FONT,
            corner_radius=8,
            command=lambda: self.search_medicines(self.search_entry.get())
        )
        search_button.pack(side="left", padx=5)
        
        clear_button = customtkinter.CTkButton(
            search_frame,
            text="🔄 Clear",
            width=100,
            height=40,
            font=MEDIUM_FONT,
            corner_radius=8,
            command=self.clear_search
        )
        clear_button.pack(side="left", padx=5)
        
        refresh_button = customtkinter.CTkButton(
            search_frame,
            text="🔄 Refresh All",
            width=120,
            height=40,
            font=MEDIUM_FONT,
            corner_radius=8,
            command=self.load_medicines_list
        )
        refresh_button.pack(side="right", padx=5)
        
        # Medicines list frame with improved styling
        list_frame = customtkinter.CTkFrame(
            main_frame,
            corner_radius=10
        )
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview with improved styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                       font=SMALL_FONT,
                       rowheight=30,
                       background="#f8f9fa",
                       fieldbackground="#f8f9fa",
                       foreground="black")
        style.configure("Treeview.Heading", 
                       font=("Arial", 11, "bold"),
                       background=self.theme["primary_color"],
                       foreground="white")
        style.map("Treeview", background=[("selected", "#007bff")])
        
        self.tree = ttk.Treeview(list_frame)
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(
            list_frame, 
            orient="vertical", 
            command=self.tree.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Configure columns with improved widths
        self.tree["columns"] = ("id", "name", "manufacturer", "price", "category", "prescription", "stock")
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("manufacturer", width=200, anchor="w")
        self.tree.column("price", width=100, anchor="e")
        self.tree.column("category", width=150, anchor="w")
        self.tree.column("prescription", width=120, anchor="center")
        self.tree.column("stock", width=100, anchor="center")
        
        # Create headings with improved labels
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Medicine Name")
        self.tree.heading("manufacturer", text="Manufacturer")
        self.tree.heading("price", text="Price (Rs)")
        self.tree.heading("category", text="Category")
        self.tree.heading("prescription", text="Rx Required")
        self.tree.heading("stock", text="Stock Qty")
        
        # Bind double click to show details
        self.tree.bind("<Double-1>", self.show_medicine_details)
    
    def load_medicines_list(self):
        """Load all medicines into the treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            medicines = Medicine.read_all_medicines()
            if not medicines:
                messagebox.showinfo("Info", "No medicines found in database")
                return
                
            for med in medicines:
                self.tree.insert("", "end", values=(
                    med["medicine_id"],
                    med["name"],
                    med["manufacturer"],
                    f"{med['price']:.2f}",
                    med["category"],
                    "Yes" if med["requires_prescription"] else "No",
                    med.get("total_stock", "N/A")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load medicines: {str(e)}")
    
    def search_medicines(self, search_term):
        """Search medicines by name, manufacturer or category"""
        if not search_term.strip():
            self.load_medicines_list()
            return
            
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            results = Medicine.search_medicines(search_term)
            if not results:
                messagebox.showinfo("Info", "No matching medicines found")
                return
                
            for med in results:
                self.tree.insert("", "end", values=(
                    med["medicine_id"],
                    med["name"],
                    med["manufacturer"],
                    f"{med['price']:.2f}",
                    med["category"],
                    "Yes" if med["requires_prescription"] else "No",
                    med.get("stock", "N/A")
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
    
    def clear_search(self):
        """Clear search results and show all medicines"""
        self.search_entry.delete(0, "end")
        self.load_medicines_list()
    
    def show_add_dialog(self):
        """Show dialog to add new medicine"""
        dialog = customtkinter.CTkToplevel(self.window)
        dialog.title("Add New Medicine")
        dialog.geometry("600x700")
        dialog.grab_set()
        
        # Create scrollable frame
        scroll_frame = customtkinter.CTkScrollableFrame(dialog)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = customtkinter.CTkLabel(
            scroll_frame,
            text="ADD NEW MEDICINE",
            font=("Arial", 16, "bold"),
            text_color=self.theme["primary_color"]
        )
        title_label.pack(pady=(0, 20))
        
        # Form fields with improved layout
        fields = [
            ("Name", "name", True),
            ("Manufacturer", "manufacturer", True),
            ("Price", "price", True),
            ("Category", "category", True),
            ("Description", "description", False),
            ("Dosage", "dosage", False)
        ]
        
        entries = {}
        for label, field, required in fields:
            frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=(5, 0))
            
            lbl = customtkinter.CTkLabel(
                frame, 
                text=f"{label}:",
                font=MEDIUM_FONT
            )
            lbl.pack(side="left")
            if required:
                req_lbl = customtkinter.CTkLabel(
                    frame, 
                    text="*", 
                    text_color="red",
                    font=MEDIUM_FONT
                )
                req_lbl.pack(side="left")
            
            entry = customtkinter.CTkEntry(
                scroll_frame,
                font=MEDIUM_FONT,
                height=40,
                corner_radius=8
            )
            entry.pack(fill="x", padx=10, pady=(0, 15))
            entries[field] = entry
        
        # Prescription checkbox with improved styling
        rx_var = customtkinter.StringVar(value="off")
        rx_check = customtkinter.CTkCheckBox(
            scroll_frame,
            text="Requires Prescription",
            variable=rx_var,
            onvalue="on",
            offvalue="off",
            font=MEDIUM_FONT,
            corner_radius=6
        )
        rx_check.pack(pady=(10, 20))

        
        
        # Add button with improved styling
        button_frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        add_btn = customtkinter.CTkButton(
            button_frame,
            text="➕ Add Medicine",
            font=("Arial", 14, "bold"),
            height=45,
            corner_radius=8,
            fg_color="#28a745",
            hover_color="#218838",
            command=lambda: self.add_medicine(
                entries["name"].get(),
                entries["manufacturer"].get(),
                entries["price"].get() if validate_price(entries["price"].get()) else "Invalid price",
                entries["category"].get(),
                entries["description"].get(),
                entries["dosage"].get(),
                rx_var.get() == "on",
                dialog
            )
        )
        add_btn.pack(fill="x", padx=50)
    
    def add_medicine(self, name, manufacturer, price, category, description, dosage, rx_required, dialog):
        """Add new medicine to database"""
        if not all([name, manufacturer, price, category]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
            
        try:
            # Create medicine
            med = Medicine(
                name=name,
                manufacturer=manufacturer,
                price=float(price),
                category=category,
                description=description if description else None,
                dosage=dosage if dosage else None,
                requires_prescription=rx_required
            )
            
            # Add to database
            med.add_in_db()
            
            messagebox.showinfo("Success", "Medicine added successfully!")
            self.load_medicines_list()
            dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine: {str(e)}")
    
    def show_update_dialog(self):
        """Show dialog to update selected medicine"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine to update")
            return
        
        item = self.tree.item(selected)
        med_id = item['values'][0]
        med_name = item['values'][1]

        try:
            # Get the medicine object
            med = Medicine.get_medicine_by_id(med_id)
            if not med:
                messagebox.showerror("Error", "Medicine not found")
                return
            
            dialog = customtkinter.CTkToplevel(self.window)
            dialog.title(f"Update Medicine: {med_name}")
            dialog.geometry("600x700")
            dialog.grab_set()
    
            # Create scrollable frame
            scroll_frame = customtkinter.CTkScrollableFrame(dialog)
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
            # Title
            title_label = customtkinter.CTkLabel(
            scroll_frame,
            text=f"UPDATE MEDICINE: {med_name}",
            font=("Arial", 16, "bold"),
            text_color=self.theme["primary_color"]
            )
            title_label.pack(pady=(0, 20))
    
            # Form fields with current values - USING NAME MANGLED ATTRIBUTES
            fields = [
            ("Name", "name", med._Medicine__name, False),
            ("Manufacturer", "manufacturer", med._Medicine__manufacturer, False),
            ("Price", "price", str(med._Medicine__price), True),
            ("Category", "category", med._Medicine__category, True),
            ("Description", "description", med._Medicine__description or "", False),
            ("Dosage", "dosage", med._Medicine__dosage or "", False)
            ]
    
            entries = {}
            for label, field, value, required in fields:
                frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
                frame.pack(fill="x", padx=10, pady=(5, 0))
        
                lbl = customtkinter.CTkLabel(
                frame, 
                text=f"{label}:",
                font=MEDIUM_FONT
                )
                lbl.pack(side="left")
                if required:
                    req_lbl = customtkinter.CTkLabel(
                    frame, 
                    text="*", 
                    text_color="red",
                    font=MEDIUM_FONT
                    )
                    req_lbl.pack(side="left")
        
                entry = customtkinter.CTkEntry(
                scroll_frame,
                font=MEDIUM_FONT,
                height=40,
                corner_radius=8
                )
                entry.insert(0, value)


                if label == "Name" or label == "Manufacturer":
                    entry.configure(state="disabled")  # Disable the entry for Name and Manufacturer
                entry.pack(fill="x", padx=10, pady=(0, 15))
                entries[field] = entry


    

            # Prescription checkbox - USING NAME MANGLED ATTRIBUTE
            rx_var = customtkinter.StringVar(value="on" if med._Medicine__requires_prescription else "off")
            rx_check = customtkinter.CTkCheckBox(
            scroll_frame,
            text="Requires Prescription",
            variable=rx_var,
            onvalue="on",
            offvalue="off",
            font=MEDIUM_FONT,
            corner_radius=6
            )
            rx_check.pack(pady=(10, 20))
    
            # Update button
            button_frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=(10, 0))
    
            update_btn = customtkinter.CTkButton(
            button_frame,
            text="💾 Save Changes",
            font=("Arial", 14, "bold"),
            height=45,
            corner_radius=8,
            fg_color="#17a2b8",
            hover_color="#138496",
            command=lambda: self.update_medicine(
                med_id,
                entries["name"].get(),
                entries["manufacturer"].get(),
                entries["price"].get() if validate_price(entries["price"].get()) else "Invalid price",
                entries["category"].get(),
                entries["description"].get(),
                entries["dosage"].get(),
                rx_var.get() == "on",
                dialog
            )
            )
            update_btn.pack(fill="x", padx=50)
    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load medicine: {str(e)}") 


    def update_medicine(self, med_id, name, manufacturer, price, category, description, dosage, rx_required, dialog):
        """Update medicine in database"""
        if not all([name, manufacturer, price, category]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
        
        try:
            # First get the existing medicine from database
            existing_med = Medicine.get_medicine_by_id(med_id)
            print(existing_med)
            if not existing_med:
                messagebox.showerror("Error", "Medicine not found in database")
                return
            # # Update the existing medicine's attributes directly
            # existing_med._Medicine__name = name
            # existing_med._Medicine__manufacturer = manufacturer
            # existing_med._Medicine__price = float(price)
            # existing_med._Medicine__category = category
            # existing_med._Medicine__description = description if description else None
            # existing_med._Medicine__dosage = dosage if dosage else None
            # existing_med._Medicine__requires_prescription = rx_required
            
            
            # Call update_medicine() on the existing object
            existing_med.update_medicine(
            new_price=float(price),
            new_category=category,
            new_description=description if description else None,
            new_dosage=dosage if dosage else None,
            new_prescription=rx_required
            )
        
            messagebox.showinfo("Success", "Medicine updated successfully!")
            self.load_medicines_list()
            dialog.destroy()
        
        except ValueError:
            messagebox.showerror("Error", "Invalid price format. Please enter a valid number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update medicine: {str(e)}")
    
    def delete_medicine(self):
        """Delete selected medicine from database"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine to delete")
            return
            
        item = self.tree.item(selected)
        med_id, name = item['values'][0], item['values'][1]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}? This action cannot be undone."):
            return
            
        try:
            # Create temporary medicine object for deletion
            med = Medicine(name, "", 0, "")
            med.delete_medicine()
            
            messagebox.showinfo("Success", "Medicine deleted successfully")
            self.load_medicines_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete medicine: {str(e)}")
    
    def show_medicine_details(self, event):
        """Show detailed view of selected medicine"""
        selected = self.tree.focus()
        if not selected:
            return
            
        item = self.tree.item(selected)
        med_id = item['values'][0]
        
        try:
            med = Medicine.get_medicine_by_id(med_id)
            if not med:
                messagebox.showerror("Error", "Medicine not found")
                return
                
            dialog = customtkinter.CTkToplevel(self.window)
            dialog.title(f"Medicine Details - {med['name']}")
            dialog.geometry("600x500")
            dialog.grab_set()
            
            # Create scrollable frame
            scroll_frame = customtkinter.CTkScrollableFrame(dialog)
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Title
            title_label = customtkinter.CTkLabel(
                scroll_frame,
                text="MEDICINE DETAILS",
                font=("Arial", 16, "bold"),
                text_color=self.theme["primary_color"]
            )
            title_label.pack(pady=(0, 20))
            
            # Display all medicine details in a clean layout
            details = [
                ("ID:", med["medicine_id"]),
                ("Name:", med["name"]),
                ("Manufacturer:", med["manufacturer"]),
                ("Price:", f"₹{med['price']:.2f}"),
                ("Category:", med["category"]),
                ("Description:", med["description"] or "Not specified"),
                ("Dosage:", med["dosage"] or "Not specified"),
                ("Requires Prescription:", "Yes" if med["requires_prescription"] else "No")
            ]
            
            for label, value in details:
                frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
                frame.pack(fill="x", pady=(0, 15))
                
                lbl = customtkinter.CTkLabel(
                    frame, 
                    text=label, 
                    font=("Arial", 12, "bold"),
                    width=180,
                    anchor="w"
                )
                lbl.pack(side="left", padx=(0, 10))
                
                val_lbl = customtkinter.CTkLabel(
                    frame, 
                    text=value,
                    font=MEDIUM_FONT,
                    wraplength=350,
                    justify="left"
                )
                val_lbl.pack(side="left", fill="x", expand=True)
            
            # Close button
            close_btn = customtkinter.CTkButton(
                scroll_frame,
                text="Close",
                font=MEDIUM_FONT,
                height=40,
                corner_radius=8,
                command=dialog.destroy
            )
            close_btn.pack(pady=(20, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load details: {str(e)}")
    
    def show_expired_medicines(self):
        """Show expired medicines in a new window"""
        try:
            expired = Medicine.get_expired_medicines()
            if not expired:
                messagebox.showinfo("Info", "No expired medicines found")
                return
                
            self.show_report_window(
                title="⚠️ Expired Medicines Report",
                columns=["ID", "Name", "Batch", "Qty", "Expiry Date", "Price"],
                data=[(
                    m["medicine_id"],
                    m["name"],
                    m["batch_number"],
                    m["current_quantity"],
                    m["expiry_date"].strftime("%d/%m/%Y"),
                    f"Rs{m['price']:.2f}"
                ) for m in expired]
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get expired medicines: {str(e)}")
    
    def show_low_stock_dialog(self):
        """Show dialog to input low stock threshold"""
        dialog = customtkinter.CTkToplevel(self.window)
        dialog.title("Low Stock Threshold")
        dialog.geometry("400x200")
        dialog.grab_set()
        
        # Main frame
        main_frame = customtkinter.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        lbl = customtkinter.CTkLabel(
            main_frame,
            text="Enter stock threshold:",
            font=MEDIUM_FONT
        )
        lbl.pack(pady=(10, 0))
        
        threshold_entry = customtkinter.CTkEntry(
            main_frame,
            font=MEDIUM_FONT,
            height=40,
            corner_radius=8
        )
        threshold_entry.insert(0, "10")
        threshold_entry.pack(pady=10)
        
        btn = customtkinter.CTkButton(
            main_frame,
            text="Show Low Stock Medicines",
            font=MEDIUM_FONT,
            height=40,
            corner_radius=8,
            fg_color="#fd7e14",
            hover_color="#e36209",
            command=lambda: self.show_low_stock_report(threshold_entry.get(), dialog)
        )
        btn.pack(pady=(10, 0))
    
    def show_low_stock_report(self, threshold, dialog=None):
        """Show low stock medicines report"""
        try:
            threshold = int(threshold) if threshold.isdigit() else 10
            low_stock = Medicine.get_low_stock_medicines(threshold)
            
            if not low_stock:
                messagebox.showinfo("Info", f"No medicines below {threshold} units")
                if dialog:
                    dialog.destroy()
                return
                
            self.show_report_window(
                title=f"📉 Low Stock Medicines (Below {threshold})",
                columns=["ID", "Name", "Manufacturer", "Stock"],
                data=[(
                    m["medicine_id"],
                    m["name"],
                    m["manufacturer"],
                    m["total_stock"]
                ) for m in low_stock]
            )
            
            if dialog:
                dialog.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get low stock: {str(e)}")
    
    def show_nearly_expiring_dialog(self):
        """Show dialog to input days threshold for nearly expiring medicines"""
        dialog = customtkinter.CTkToplevel(self.window)
        dialog.title("Nearly Expiring Threshold")
        dialog.geometry("400x200")
        dialog.grab_set()
        
        # Main frame
        main_frame = customtkinter.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        lbl = customtkinter.CTkLabel(
            main_frame,
            text="Enter days threshold:",
            font=MEDIUM_FONT
        )
        lbl.pack(pady=(10, 0))
        
        days_entry = customtkinter.CTkEntry(
            main_frame,
            font=MEDIUM_FONT,
            height=40,
            corner_radius=8
        )
        days_entry.insert(0, "30")
        days_entry.pack(pady=10)
        
        btn = customtkinter.CTkButton(
            main_frame,
            text="Show Nearly Expiring Medicines",
            font=MEDIUM_FONT,
            height=40,
            corner_radius=8,
            fg_color="#6f42c1",
            hover_color="#5a3d8e",
            command=lambda: self.show_nearly_expiring_report(days_entry.get(), dialog)
        )
        btn.pack(pady=(10, 0))
    
    def show_nearly_expiring_report(self, days, dialog=None):
        """Show nearly expiring medicines report"""
        try:
            days = int(days) if days.isdigit() else 30
            expiring = Medicine.get_nearly_expiring_medicines(days)
            
            if not expiring:
                messagebox.showinfo("Info", f"No medicines expiring within {days} days")
                if dialog:
                    dialog.destroy()
                return
                
            self.show_report_window(
                title=f"⏳ Medicines Expiring in Next {days} Days",
                columns=["Name", "Batch", "Expiry Date", "Qty", "Days Left"],
                data=[(
                    m["name"],
                    m["batch_number"],
                    m["expiry_date"].strftime("%d/%m/%Y"),
                    m["current_quantity"],
                    m["days_left"]
                ) for m in expiring]
            )
            
            if dialog:
                dialog.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get expiring medicines: {str(e)}")
    
    def show_report_window(self, title, columns, data):
        """Generic function to show report data in a new window"""
        report_window = customtkinter.CTkToplevel(self.window)
        report_window.title(title)
        report_window.geometry("1000x600")
        
        # Main frame
        main_frame = customtkinter.CTkFrame(report_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = customtkinter.CTkLabel(
            main_frame,
            text=title,
            font=("Arial", 16, "bold"),
            text_color=self.theme["primary_color"]
        )
        title_label.pack(pady=(0, 20))
        
        # Frame for treeview
        tree_frame = customtkinter.CTkFrame(main_frame)
        tree_frame.pack(fill="both", expand=True)
        
        # Treeview with scrollbars
        style = ttk.Style()
        style.configure("Report.Treeview", 
                       font=SMALL_FONT,
                       rowheight=30,
                       background="#f8f9fa",
                       fieldbackground="#f8f9fa",
                       foreground="black")
        style.configure("Report.Treeview.Heading", 
                       font=("Arial", 11, "bold"),
                       background=self.theme["primary_color"],
                       foreground="white")
        style.map("Report.Treeview", background=[("selected", "#007bff")])
        
        tree = ttk.Treeview(tree_frame, style="Report.Treeview")
        tree.pack(side="left", fill="both", expand=True)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        hsb.pack(side="bottom", fill="x")
        
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Configure columns
        tree["columns"] = [f"col{i}" for i in range(len(columns))]
        tree.column("#0", width=0, stretch=False)
        
        for i, col in enumerate(columns):
            tree.column(f"col{i}", width=150, anchor="w")
            tree.heading(f"col{i}", text=col)
        
        # Add data
        for row in data:
            tree.insert("", "end", values=row)
        
        # Close button
        close_btn = customtkinter.CTkButton(
            main_frame,
            text="Close Report",
            font=MEDIUM_FONT,
            height=40,
            corner_radius=8,
            command=report_window.destroy
        )
        close_btn.pack(pady=(20, 0))
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = MedicinesWindow()
    app.run()