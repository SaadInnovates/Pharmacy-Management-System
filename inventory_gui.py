# inventory_gui.py
import customtkinter
from tkinter import messagebox, ttk
from theme import setup_theme
from inventory import PharmacyInventory
from datetime import datetime

# Set custom font styles
LARGE_FONT = ("Arial", 14)
MEDIUM_FONT = ("Arial", 12)
SMALL_FONT = ("Arial", 10)

class InventoryWindow:
    def __init__(self):
        self.theme = setup_theme()
        self.inventory = PharmacyInventory()
        
        self.window = customtkinter.CTk()
        self.window.title("Pharmacy Management System - Inventory")
        self.window.geometry("1400x900")
        
        # Configure grid layout
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        self.create_widgets()
        self.load_inventory_list()
        
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
            text="INVENTORY MANAGEMENT",
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
            text="➕ Add Item",
            fg_color="#28a745",
            hover_color="#218838",
            command=self.show_add_dialog,
            **button_style
        )
        add_button.pack(side="left", padx=5)
        
        update_button = customtkinter.CTkButton(
            action_frame,
            text="✏️ Update Qty",
            fg_color="#17a2b8",
            hover_color="#138496",
            command=self.show_update_dialog,
            **button_style
        )
        update_button.pack(side="left", padx=5)
        
        transfer_button = customtkinter.CTkButton(
            action_frame,
            text="🔄 Transfer",
            fg_color="#6f42c1",
            hover_color="#5a3d8e",
            command=self.show_transfer_dialog,
            **button_style
        )
        transfer_button.pack(side="left", padx=5)


        delete_button = customtkinter.CTkButton(
            action_frame,
            text="🗑️ Delete",
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self.show_delete_dialog,
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
        
        low_stock_button = customtkinter.CTkButton(
            reports_frame,
            text="📉 Low Stock",
            fg_color="#fd7e14",
            hover_color="#e36209",
            command=self.show_low_stock,
            **report_button_style
        )
        low_stock_button.pack(side="left", padx=5)
        
        expiring_button = customtkinter.CTkButton(
            reports_frame,
            text="⏳ Expiring Soon",
            fg_color="#ffc107",
            hover_color="#e0a800",
            text_color="black",
            command=self.show_expiring_soon,
            **report_button_style
        )
        expiring_button.pack(side="left", padx=5)
        
        report_button = customtkinter.CTkButton(
            reports_frame,
            text="📊 Full Report",
            fg_color="#20c997",
            hover_color="#1aa179",
            command=self.show_report,
            **report_button_style
        )
        report_button.pack(side="left", padx=5)
        
        # Search frame with improved styling
        search_frame = customtkinter.CTkFrame(
            main_frame, 
            fg_color="transparent"
        )
        search_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        self.search_entry = customtkinter.CTkEntry(
            search_frame,
            placeholder_text="Search inventory by medicine, batch or location...",
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
            command=self.search_inventory
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
            command=self.load_inventory_list
        )
        refresh_button.pack(side="right", padx=5)
        
        # Inventory list frame with improved styling
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
        self.tree["columns"] = ("id", "medicine", "supplier", "batch", "quantity", "expiry", "location")
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("medicine", width=250, anchor="w")
        self.tree.column("supplier", width=150, anchor="w")
        self.tree.column("batch", width=120, anchor="center")
        self.tree.column("quantity", width=80, anchor="center")
        self.tree.column("expiry", width=120, anchor="center")
        self.tree.column("location", width=120, anchor="center")
        
        # Create headings with improved labels
        self.tree.heading("id", text="ID")
        self.tree.heading("medicine", text="Medicine")
        self.tree.heading("supplier", text="Supplier ID")
        self.tree.heading("batch", text="Batch No.")
        self.tree.heading("quantity", text="Qty")
        self.tree.heading("expiry", text="Expiry Date")
        self.tree.heading("location", text="Location")
        
        # Bind double click to show details
        self.tree.bind("<Double-1>", self.show_item_details)
    
    def load_inventory_list(self):
        """Load all inventory items into the treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            self.inventory.cursor.execute("""
                SELECT i.inventory_id, m.name, i.supplier_id, i.batch_number, 
                       i.current_quantity, i.expiry_date, i.location
                FROM inventory i
                JOIN medicines m ON i.medicine_id = m.medicine_id
                ORDER BY i.expiry_date
            """)
            items = self.inventory.cursor.fetchall()
            
            if not items:
                messagebox.showinfo("Info", "No inventory items found")
                return
                
            for item in items:
                self.tree.insert("", "end", values=(
                    item["inventory_id"],
                    item["name"],
                    item["supplier_id"],
                    item["batch_number"],
                    item["current_quantity"],
                    item["expiry_date"].strftime("%Y-%m-%d") if item["expiry_date"] else "N/A",
                    item["location"]
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {str(e)}")
    
    def search_inventory(self):
        """Search inventory by medicine, batch or location"""
        search_term = self.search_entry.get()
        if not search_term.strip():
            self.load_inventory_list()
            return
            
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            self.inventory.cursor.execute("""
                SELECT i.inventory_id, m.name, i.supplier_id, i.batch_number, 
                       i.current_quantity, i.expiry_date, i.location
                FROM inventory i
                JOIN medicines m ON i.medicine_id = m.medicine_id
                WHERE m.name LIKE %s OR i.batch_number LIKE %s OR i.location LIKE %s
                ORDER BY i.expiry_date
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            items = self.inventory.cursor.fetchall()
            
            if not items:
                messagebox.showinfo("Info", "No matching items found")
                return
                
            for item in items:
                self.tree.insert("", "end", values=(
                    item["inventory_id"],
                    item["name"],
                    item["supplier_id"],
                    item["batch_number"],
                    item["current_quantity"],
                    item["expiry_date"].strftime("%Y-%m-%d") if item["expiry_date"] else "N/A",
                    item["location"]
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
    
    def clear_search(self):
        """Clear search results and show all inventory items"""
        self.search_entry.delete(0, "end")
        self.load_inventory_list()
    
    def show_add_dialog(self):
        """Show dialog to add new inventory item"""
        dialog = customtkinter.CTkToplevel(self.window)
        dialog.title("Add Inventory Item")
        dialog.geometry("500x600")
        dialog.grab_set()
        
        # Create scrollable frame
        scroll_frame = customtkinter.CTkScrollableFrame(dialog)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = customtkinter.CTkLabel(
            scroll_frame,
            text="ADD INVENTORY ITEM",
            font=("Arial", 16, "bold"),
            text_color=self.theme["primary_color"]
        )
        title_label.pack(pady=(0, 20))
        
        # Form fields
        fields = [
            ("Medicine Name", "medicine"),
            ("Supplier ID", "supplier"),
            ("Quantity", "quantity"),
            ("Batch Number", "batch"),
            ("Expiry Date (YYYY-MM-DD)", "expiry"),
            ("Location", "location")
        ]
        
        entries = {}
        for label, field in fields:
            frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=(5, 0))
            
            lbl = customtkinter.CTkLabel(
                frame, 
                text=f"{label}:",
                font=MEDIUM_FONT
            )
            lbl.pack(side="left")
            
            if field in ["supplier", "quantity"]:
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
        
        # Add button
        button_frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        add_btn = customtkinter.CTkButton(
            button_frame,
            text="➕ Add Item",
            font=("Arial", 14, "bold"),
            height=45,
            corner_radius=8,
            fg_color="#28a745",
            hover_color="#218838",
            command=lambda: self.add_inventory_item(
                entries["medicine"].get(),
                entries["supplier"].get(),
                entries["quantity"].get(),
                entries["batch"].get(),
                entries["expiry"].get(),
                entries["location"].get(),
                dialog
            )
        )
        add_btn.pack(fill="x", padx=50)
    
    def add_inventory_item(self, medicine_name, supplier_id, quantity, batch, expiry, location, dialog):
        """Add new inventory item to database"""
        if not all([medicine_name, supplier_id, quantity, expiry]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
            
        try:
            from medicines import Medicine
            medicine_id = Medicine.get_id_by_name(medicine_name)
            if not medicine_id:
                messagebox.showerror("Error", "Medicine not found")
                return
                
            result = self.inventory.add_inventory_item(
                medicine_id,
                int(supplier_id),
                int(quantity),
                batch,
                expiry,
                location
            )
            
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
                self.load_inventory_list()
                dialog.destroy()
            else:
                messagebox.showerror("Error", result["message"])
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for IDs and quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")
    
    def show_update_dialog(self):
        """Show dialog to update inventory quantity"""
        selected = self.get_selected_item()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item first")
            return
            
        dialog = customtkinter.CTkToplevel(self.window)
        dialog.title("Update Inventory Quantity")
        dialog.geometry("400x250")
        dialog.grab_set()
        
        # Main frame
        main_frame = customtkinter.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Current info
        info_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 15))
        
        customtkinter.CTkLabel(
            info_frame,
            text=f"Medicine: {selected['name']}",
            font=MEDIUM_FONT
        ).pack(anchor="w")
        
        customtkinter.CTkLabel(
            info_frame,
            text=f"Current Quantity: {selected['current_quantity']}",
            font=MEDIUM_FONT
        ).pack(anchor="w")
        
        # New quantity
        customtkinter.CTkLabel(
            main_frame,
            text="New Quantity:",
            font=MEDIUM_FONT
        ).pack(anchor="w", pady=(10, 0))
        
        quantity_entry = customtkinter.CTkEntry(
            main_frame,
            font=MEDIUM_FONT,
            height=40,
            corner_radius=8
        )
        quantity_entry.pack(fill="x", pady=(0, 20))
        
        # Update button
        update_btn = customtkinter.CTkButton(
            main_frame,
            text="💾 Update Quantity",
            font=("Arial", 14, "bold"),
            height=45,
            corner_radius=8,
            fg_color="#17a2b8",
            hover_color="#138496",
            command=lambda: self.update_inventory_quantity(
                selected['inventory_id'],
                quantity_entry.get(),
                dialog
            )
        )
        update_btn.pack(fill="x")
    
    def update_inventory_quantity(self, inventory_id, new_quantity, dialog):
        """Update inventory quantity in database"""
        try:
            result = self.inventory.update_inventory_quantity(
                int(inventory_id),
                int(new_quantity)
            )
            
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
                self.load_inventory_list()
                dialog.destroy()
            else:
                messagebox.showerror("Error", result["message"])
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update quantity: {str(e)}")
    
    def show_transfer_dialog(self):
        """Show dialog to transfer inventory"""
        selected = self.get_selected_item()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item first")
            return
            
        dialog = customtkinter.CTkToplevel(self.window)
        dialog.title("Transfer Inventory")
        dialog.geometry("450x350")
        dialog.grab_set()
        
        # Main frame
        main_frame = customtkinter.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Current info
        info_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 15))
        
        customtkinter.CTkLabel(
            info_frame,
            text=f"Medicine: {selected['name']}",
            font=MEDIUM_FONT
        ).pack(anchor="w")
        
        customtkinter.CTkLabel(
            info_frame,
            text=f"Batch: {selected['batch_number']}",
            font=MEDIUM_FONT
        ).pack(anchor="w")
        
        customtkinter.CTkLabel(
            info_frame,
            text=f"Current Location: {selected['location']}",
            font=MEDIUM_FONT
        ).pack(anchor="w")
        
        customtkinter.CTkLabel(
            info_frame,
            text=f"Available Quantity: {selected['current_quantity']}",
            font=MEDIUM_FONT
        ).pack(anchor="w")
        
        # Transfer details
        customtkinter.CTkLabel(
            main_frame,
            text="Quantity to Transfer:",
            font=MEDIUM_FONT
        ).pack(anchor="w", pady=(10, 0))
        
        quantity_entry = customtkinter.CTkEntry(
            main_frame,
            font=MEDIUM_FONT,
            height=40,
            corner_radius=8
        )
        quantity_entry.pack(fill="x", pady=(0, 10))
        
        customtkinter.CTkLabel(
            main_frame,
            text="New Location:",
            font=MEDIUM_FONT
        ).pack(anchor="w", pady=(10, 0))
        
        location_entry = customtkinter.CTkEntry(
            main_frame,
            font=MEDIUM_FONT,
            height=40,
            corner_radius=8
        )
        location_entry.pack(fill="x", pady=(0, 20))
        
        # Transfer button
        transfer_btn = customtkinter.CTkButton(
            main_frame,
            text="🔄 Transfer",
            font=("Arial", 14, "bold"),
            height=45,
            corner_radius=8,
            fg_color="#6f42c1",
            hover_color="#5a3d8e",
            command=lambda: self.transfer_inventory(
                selected['inventory_id'],
                quantity_entry.get(),
                location_entry.get(),
                dialog
            )
        )
        transfer_btn.pack(fill="x")
    
    def transfer_inventory(self, inventory_id, quantity, new_location, dialog):
        """Transfer inventory to new location"""
        try:
            result = self.inventory.transfer_inventory(
                int(inventory_id),
                new_location,
                int(quantity)
            )
            
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
                self.load_inventory_list()
                dialog.destroy()
            else:
                messagebox.showerror("Error", result["message"])
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to transfer inventory: {str(e)}")
    
    def show_item_details(self, event):
        """Show detailed view of selected inventory item"""
        selected = self.get_selected_item()
        if not selected:
            return
            
        dialog = customtkinter.CTkToplevel(self.window)
        dialog.title(f"Inventory Details - {selected['name']}")
        dialog.geometry("600x500")
        dialog.grab_set()
        
        # Create scrollable frame
        scroll_frame = customtkinter.CTkScrollableFrame(dialog)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = customtkinter.CTkLabel(
            scroll_frame,
            text="INVENTORY ITEM DETAILS",
            font=("Arial", 16, "bold"),
            text_color=self.theme["primary_color"]
        )
        title_label.pack(pady=(0, 20))
        
        # Display all details in a clean layout
        details = [
            ("ID:", selected['inventory_id']),
            ("Medicine:", selected['name']),
            ("Supplier ID:", selected['supplier_id']),
            ("Batch Number:", selected['batch_number']),
            ("Current Quantity:", selected['current_quantity']),
            ("Expiry Date:", selected['expiry_date']),
            ("Location:", selected['location'])
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
    
    def show_low_stock(self):
        """Show low stock items dialog"""
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
            text="Show Low Stock Items",
            font=MEDIUM_FONT,
            height=40,
            corner_radius=8,
            fg_color="#fd7e14",
            hover_color="#e36209",
            command=lambda: self.show_low_stock_report(threshold_entry.get(), dialog)
        )
        btn.pack(pady=(10, 0))
    
    def show_low_stock_report(self, threshold, dialog=None):
        """Show low stock items report"""
        try:
            threshold = int(threshold) if threshold.isdigit() else 10
            items = self.inventory.get_low_stock_items(threshold)
            
            if isinstance(items, dict) and "error" in items:
                messagebox.showerror("Error", items["error"])
                if dialog:
                    dialog.destroy()
                return
                
            if not items:
                messagebox.showinfo("Info", f"No items below {threshold} units")
                if dialog:
                    dialog.destroy()
                return
                
            self.show_report_window(
                title=f"📉 Low Stock Items (Below {threshold})",
                columns=["ID", "Medicine", "Quantity", "Location", "Supplier"],
                data=[(
                    item["inventory_id"],
                    item["medicine_name"],
                    item["current_quantity"],
                    item["location"],
                    item["supplier_id"]
                ) for item in items]
            )
            
            if dialog:
                dialog.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get low stock: {str(e)}")
    
    def show_expiring_soon(self):
        """Show expiring soon items dialog"""
        dialog = customtkinter.CTkToplevel(self.window)
        dialog.title("Expiring Soon Threshold")
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
            text="Show Expiring Items",
            font=MEDIUM_FONT,
            height=40,
            corner_radius=8,
            fg_color="#ffc107",
            hover_color="#e0a800",
            text_color="black",
            command=lambda: self.show_expiring_report(days_entry.get(), dialog)
        )
        btn.pack(pady=(10, 0))
    
    def show_expiring_report(self, days, dialog=None):
        """Show expiring soon items report"""
        try:
            days = int(days) if days.isdigit() else 30
            items = self.inventory.get_expiring_soon(days)
            
            if isinstance(items, dict) and "error" in items:
                messagebox.showerror("Error", items["error"])
                if dialog:
                    dialog.destroy()
                return
                
            if not items:
                messagebox.showinfo("Info", f"No items expiring within {days} days")
                if dialog:
                    dialog.destroy()
                return
                
            self.show_report_window(
                title=f"⏳ Items Expiring in {days} Days",
                columns=["ID", "Medicine", "Quantity", "Expiry Date", "Days Left", "Location"],
                data=[(
                    item["inventory_id"],
                    item["medicine_name"],
                    item["current_quantity"],
                    item["expiry_date"].strftime("%Y-%m-%d") if item["expiry_date"] else "N/A",
                    item["days_until_expiry"],
                    item["location"]
                ) for item in items]
            )
            
            if dialog:
                dialog.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get expiring items: {str(e)}")
    
    def show_report(self):
        """Generate and show full inventory report"""
        try:
            report = self.inventory.generate_inventory_report()
            
            if "error" in report:
                messagebox.showerror("Error", report["error"])
                return
                
            self.show_report_window(
                title="📊 Full Inventory Report",
                columns=["Medicine", "Total Qty", "Batches", "Earliest Expiry", "Locations"],
                data=[(
                    item["medicine_name"],
                    item["total_quantity"],
                    item["batch_count"],
                    item["earliest_expiry"].strftime("%Y-%m-%d") if item["earliest_expiry"] else "N/A",
                    item["locations"]
                ) for item in report["report"]],
                summary={
                    "Total Items": report["summary"]["total_items"],
                    "Unique Medicines": report["summary"]["unique_medicines"],
                    "Expiring Soon": report["summary"]["items_expiring_soon"]
                }
            )
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def show_report_window(self, title, columns, data, summary=None):
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
        
        # Summary frame if provided
        if summary:
            summary_frame = customtkinter.CTkFrame(
                main_frame,
                fg_color="#e9ecef",
                corner_radius=8
            )
            summary_frame.pack(fill="x", pady=(0, 15))
            
            summary_text = " | ".join(f"{k}: {v}" for k, v in summary.items())
            customtkinter.CTkLabel(
                summary_frame,
                text=summary_text,
                font=("Arial", 12, "bold"),
                text_color="#495057"
            ).pack(padx=10, pady=5)
        
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
    
    def get_selected_item(self):
        """Get currently selected inventory item"""
        selected = self.tree.focus()
        if not selected:
            return None
            
        item = self.tree.item(selected)
        values = item['values']
        
        return {
            'inventory_id': values[0],
            'name': values[1],
            'supplier_id': values[2],
            'batch_number': values[3],
            'current_quantity': values[4],
            'expiry_date': values[5],
            'location': values[6]
        }
    

    def show_delete_dialog(self):
        """Show confirmation dialog for deleting inventory item"""
        selected = self.get_selected_item()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item first")
            return
            
        # Confirm deletion
        response = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete:\n\n"
            f"Medicine: {selected['name']}\n"
            f"Batch: {selected['batch_number']}\n"
            f"Quantity: {selected['current_quantity']}\n\n"
            "This action cannot be undone!",
            parent=self.window
        )
        
        if response:
            self.delete_inventory_item(selected['inventory_id'])
    
    def delete_inventory_item(self, inventory_id):
        """Delete inventory item from database"""
        try:
            result = self.inventory.delete_inventory_item(inventory_id)
            
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
                self.load_inventory_list()
            else:
                messagebox.showerror("Error", result["message"])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
    
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = InventoryWindow()
    app.run()