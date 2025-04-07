# prescriptions_gui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from prescriptions import PrescriptionManager
from medicines import Medicine
from theme import setup_theme
import mysql.connector
from database import get_db_connection

class PrescriptionGUI:


    def __init__(self, root):
        self.root = root
        self.root.title("PharmaCare - Prescription Management")
        self.pm = PrescriptionManager()
        self.current_prescription_id = None
        self.connection = get_db_connection()
    
        # Setup theme and colors
        self.theme = setup_theme()
        self.setup_styles()
    
        # Configure main window
        self.root.geometry("1024x768")
        self.root.minsize(800,600)
        self.root.configure(bg=self.theme["bg_color"])
    
        # Create main container with gradient background
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Header with logo, title and save button
        self.header = ttk.Frame(self.main_frame, style='Header.TFrame')
        self.header.pack(fill=tk.X, pady=(0, 15))
    
        # Pharmacy logo placeholder (can be replaced with actual image)
        self.logo_label = ttk.Label(
        self.header,
        text="💊",
        font=("Arial", 24),
        foreground=self.theme["primary_color"]
        )
        self.logo_label.pack(side=tk.LEFT, padx=10)
    
        ttk.Label(
        self.header,
        text="PharmaCare Prescription Management",
        font=("Helvetica", 18, "bold"),
        foreground=self.theme["primary_color"]
        ).pack(side=tk.LEFT)
    
        # # Add save button to the header
        # self.top_save_button = ttk.Button(
        # self.header,
        # text="💾 Save",
        # command=self.save_current_prescription,
        # style='Accent.TButton',
        # padding=5
        # )
        # self.top_save_button.pack(side=tk.RIGHT, padx=10)
    
        # Create notebook for tabs with modern styling
        style = ttk.Style()
        style.configure('TNotebook', background=self.theme["bg_color"])
        style.configure('TNotebook.Tab', 
                  font=("Helvetica", 11, "bold"),
                  padding=[15, 5],
                  background=self.theme["bg_color"],
                  foreground=self.theme["text_primary"])
        style.map('TNotebook.Tab', 
             background=[('selected', self.theme["primary_color"])],
             foreground=[('selected', 'white')])
    
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
        # Create tabs
        self.create_tab = ttk.Frame(self.notebook)
        self.view_tab = ttk.Frame(self.notebook)
        self.search_tab = ttk.Frame(self.notebook)
    
        self.notebook.add(self.create_tab, text="➕ Create Prescription")
        self.notebook.add(self.view_tab, text="🔍 View/Edit Prescriptions")
        self.notebook.add(self.search_tab, text="🔎 Search Prescriptions")
    
        # Initialize tabs
        self.setup_create_tab()
        self.setup_view_tab()
        self.setup_search_tab()
    
        # Status bar with modern styling
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
        self.main_frame, 
        textvariable=self.status_var,
        relief=tk.SUNKEN,
        anchor=tk.W,
        style='Status.TLabel',
        padding=8,
        font=("Helvetica", 9, "italic")
        )
        self.status_bar.pack(fill=tk.X, pady=(5,0))
        self.update_status("System ready. Welcome to PharmaCare!")

    # Add the save_current_prescription method
    def save_current_prescription(self):
        """Handle save button at top of window"""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # Create tab
            self.create_prescription()
        elif current_tab == 1:  # View/Edit tab
            if self.current_prescription_id:
                self.save_prescription_changes()
            else:
                messagebox.showwarning("Warning", "No prescription loaded to save")
        else:  # Search tab
            messagebox.showinfo("Info", "No prescription to save in Search tab")
    
    def setup_styles(self):
    
        """Setup custom styles using theme colors"""
        style = ttk.Style()
        style.theme_use('clam')
    
        # Get theme colors
        theme = setup_theme()
        primary_color = theme["primary_color"]
        secondary_color = theme["secondary_color"]
        error_color = theme["error_color"]
        text_primary = theme["text_primary"]
        text_secondary = theme["text_secondary"]
        bg_color = theme["bg_color"]
        entry_bg = theme["entry_bg"]
    
        # Create darker variants for active states
        primary_dark = "#3a6cb5"  # Darker shade of primary_color (#4B89DC)
        secondary_dark = "#3da766"  # Darker shade of secondary_color (#50C878)
        error_dark = "#d45959"  # Darker shade of error_color (#FF6B6B)
    
        # Base styles
        style.configure('.', 
                  background=bg_color,
                  foreground=text_primary)
    
        style.configure('TFrame', 
                  background=bg_color,
                  borderwidth=0)
    
        style.configure('TLabel', 
                  background=bg_color,
                  font=theme["font_body"],
                  foreground=text_primary)
    
        style.configure('TButton', 
                  font=theme["font_button"],
                  padding=10,
                  relief=tk.RAISED,
                  borderwidth=2)
    
        style.configure('TEntry', 
                  font=theme["font_body"],
                  padding=5,
                  relief=tk.SOLID,
                  borderwidth=1,
                  fieldbackground=entry_bg)
    
        style.configure('Header.TFrame', 
                  background=bg_color,
                  relief=tk.FLAT)
    
        style.configure('Status.TLabel', 
                  font=theme["font_body"],
                  foreground=text_secondary,
                  background="#f0f0f0")
    
        style.configure('Treeview', 
                  font=theme["font_body"],
                  rowheight=30,
                  fieldbackground=entry_bg,
                  background="white",
                  foreground="black")
    
        style.configure('Treeview.Heading', 
                  font=theme["font_button"],
                  background=primary_color,
                  foreground="white",
                  relief=tk.FLAT)
    
        style.configure('Card.TLabelframe', 
                  background=bg_color,
                  borderwidth=2,
                  relief=tk.GROOVE,
                  labelmargins=10)
    
        style.configure('Card.TLabelframe.Label', 
                  background=bg_color,
                  font=theme["font_subtitle"],
                  foreground=primary_color)
    
        # Button styles with hover effects - CORRECTED VERSION
        style.configure('Accent.TButton', 
                  background=primary_color,
                  foreground="white")
        style.map('Accent.TButton',
             background=[('active', primary_dark)])
    
        style.configure('Secondary.TButton', 
                  background=secondary_color,
                  foreground="white")
        style.map('Secondary.TButton',
             background=[('active', secondary_dark)])
    
        style.configure('Danger.TButton', 
                  background=error_color,
                  foreground="white")
        style.map('Danger.TButton',
             background=[('active', error_dark)])
    
    def update_status(self, message):
        self.status_var.set(message)
        self.root.after(5000, lambda: self.status_var.set("Ready"))
    
    def setup_create_tab(self):
        # Main container with padding
        create_container = ttk.Frame(self.create_tab)
        create_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Prescription info card
        info_frame = ttk.LabelFrame(
            create_container, 
            text=" Prescription Information ",
            style='Card.TLabelframe'
        )
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Date field with calendar icon
        date_frame = ttk.Frame(info_frame)
        date_frame.pack(fill=tk.X, pady=5)
        ttk.Label(date_frame, text="📅 Date:", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Label(date_frame, textvariable=self.date_var, font=("Helvetica", 10)).pack(side=tk.LEFT, padx=10)
        

        ttk.Button(
        date_frame, 
        text="💾 Save Prescription", 
        command=self.create_prescription,
        style='Accent.TButton',
        padding=10
        ).pack(side=tk.LEFT, padx=(10, 0))


        # Medicines card with modern styling
        meds_frame = ttk.LabelFrame(
            create_container, 
            text=" 💊 Prescription Items ",
            style='Card.TLabelframe'
        )
        meds_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview with striped rows
        self.meds_tree = ttk.Treeview(
            meds_frame, 
            columns=('name', 'qty', 'price', 'total'), 
            show='headings',
            style='Custom.Treeview'
        )
        
        # Configure columns with proper alignment
        self.meds_tree.heading('name', text='Medicine Name', anchor=tk.W)
        self.meds_tree.heading('qty', text='Quantity', anchor=tk.CENTER)
        self.meds_tree.heading('price', text='Unit Price', anchor=tk.E)
        self.meds_tree.heading('total', text='Total Price', anchor=tk.E)
        
        self.meds_tree.column('name', width=300, anchor=tk.W)
        self.meds_tree.column('qty', width=100, anchor=tk.CENTER)
        self.meds_tree.column('price', width=150, anchor=tk.E)
        self.meds_tree.column('total', width=150, anchor=tk.E)
        
        # Add scrollbar with modern styling
        scrollbar = ttk.Scrollbar(
            meds_frame, 
            orient=tk.VERTICAL, 
            command=self.meds_tree.yview
        )
        self.meds_tree.configure(yscroll=scrollbar.set)
        
        # Grid layout for treeview and scrollbar
        self.meds_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Configure grid weights
        meds_frame.grid_rowconfigure(0, weight=1)
        meds_frame.grid_columnconfigure(0, weight=1)
        
        # Action buttons with icons
        btn_frame = ttk.Frame(meds_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(15, 0), sticky='ew')
        
        ttk.Button(
            btn_frame, 
            text="➕ Add Medicine", 
            command=self.add_medicine,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5, ipadx=10)
        
        ttk.Button(
            btn_frame, 
            text="➖ Remove Selected", 
            command=self.remove_medicine,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5, ipadx=10)
        
        # Total amount display with emphasis
        total_frame = ttk.Frame(create_container)
        total_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(
            total_frame, 
            text="Total Amount:", 
            font=("Helvetica", 12, "bold")
        ).pack(side=tk.LEFT)
        
        self.total_var = tk.StringVar(value="0.00")
        ttk.Label(
            total_frame, 
            textvariable=self.total_var, 
            font=("Helvetica", 12, "bold"),
            foreground=self.theme["primary_color"]
        ).pack(side=tk.LEFT, padx=10)
        
        
    
    def setup_view_tab(self):
        """Setup the View/Edit Prescription tab with consistent geometry management"""
        # Main container
        view_container = ttk.Frame(self.view_tab)
        view_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Search frame - using pack
        search_frame = ttk.LabelFrame(
        view_container,
        text=" 🔍 Search Prescription ",
        style='Card.TLabelframe'
        )
        search_frame.pack(fill=tk.X, pady=(0, 15))

        # Search widgets - all using pack
        ttk.Label(search_frame, text="Prescription ID:").pack(side=tk.LEFT)
        self.search_id_entry = ttk.Entry(search_frame, width=15)
        self.search_id_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(
        search_frame,
        text="Search",
        command=self.search_prescription,
        style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)

        # Button frame - now inside the search_frame
        btn_frame = ttk.Frame(search_frame)
        btn_frame.pack(side=tk.LEFT, padx=20)

        ttk.Button(
        btn_frame,
        text="➕ Add",
        command=self.add_medicine_to_existing,
        style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
        btn_frame,
        text="➖ Remove",
        command=self.remove_medicine_from_existing,
        style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
        btn_frame,
        text="✏️ Qty",
        command=self.update_medicine_quantity,
        style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=2)


        ttk.Button(
        btn_frame,
        text="🗑️ Delete",
        command=self.delete_prescription,
        style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=2)

        # Details frame - using pack
        details_frame = ttk.LabelFrame(
        view_container,
        text=" 📝 Prescription Details ",
        style='Card.TLabelframe'
        )
        details_frame.pack(fill=tk.BOTH, expand=True)

        # Info frame - using pack
        info_frame = ttk.Frame(details_frame)
        info_frame.pack(fill=tk.X, pady=(0, 15))

        # Info labels - using pack
        ttk.Label(info_frame, text="🆔 ID:", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        self.view_id_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.view_id_var).pack(side=tk.LEFT, padx=10)

        ttk.Label(info_frame, text="📅 Date:", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        self.view_date_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.view_date_var).pack(side=tk.LEFT, padx=10)

        ttk.Label(info_frame, text="💰 Total:", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        self.view_total_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.view_total_var).pack(side=tk.LEFT, padx=10)

        # Treeview container - using pack
        tree_container = ttk.Frame(details_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # Treeview and scrollbar - using grid within their own container
        self.view_meds_tree = ttk.Treeview(
        tree_container,
        columns=('name', 'qty', 'price', 'total'),
        show='headings'
        )

        self.view_meds_tree.heading('name', text='Medicine Name', anchor=tk.W)
        self.view_meds_tree.heading('qty', text='Quantity', anchor=tk.CENTER)
        self.view_meds_tree.heading('price', text='Unit Price', anchor=tk.E)
        self.view_meds_tree.heading('total', text='Total Price', anchor=tk.E)

        self.view_meds_tree.column('name', width=300, anchor=tk.W)
        self.view_meds_tree.column('qty', width=100, anchor=tk.CENTER)
        self.view_meds_tree.column('price', width=150, anchor=tk.E)
        self.view_meds_tree.column('total', width=150, anchor=tk.E)

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.view_meds_tree.yview)
        self.view_meds_tree.configure(yscroll=scrollbar.set)

        self.view_meds_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)


    def edit_prescription(self):
        """Enable editing of prescription details"""
        if not self.current_prescription_id:
            messagebox.showwarning("Warning", "Please search for a prescription first")
            return
    
        # Create edit dialog
        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title(f"Edit Prescription #{self.current_prescription_id}")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
    
        # Get current prescription details
        prescription = self.get_prescription_details(self.current_prescription_id)
        if not prescription:
            messagebox.showerror("Error", "Could not load prescription details")
            edit_dialog.destroy()
            return
    
        # Date frame
        date_frame = ttk.Frame(edit_dialog, padding="10")
        date_frame.pack(fill=tk.X)
    
        ttk.Label(date_frame, text="Date:").pack(side=tk.LEFT)
        self.edit_date_var = tk.StringVar(value=prescription['date'])
        date_entry = ttk.Entry(date_frame, textvariable=self.edit_date_var)
        date_entry.pack(side=tk.LEFT, padx=5)
    
        # Buttons frame
        buttons_frame = ttk.Frame(edit_dialog, padding="10")
        buttons_frame.pack(fill=tk.X)
    
        ttk.Button(
        buttons_frame,
        text="Save Changes",
        command=lambda: self.save_prescription_edit(edit_dialog),
        style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
    
        ttk.Button(
        buttons_frame,
        text="Cancel",
        command=edit_dialog.destroy,
        style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=5)



    def save_prescription_edit(self, dialog):
        """Save the edited prescription details"""
        try:
            new_date = self.edit_date_var.get()
        
            # Validate date format
            datetime.strptime(new_date, "%Y-%m-%d")
        
            # Update prescription in database
            cursor = self.connection.cursor()
            cursor.execute(
            "UPDATE PRESCRIPTIONS SET date = %s WHERE prescription_id = %s",
            (new_date, self.current_prescription_id)
            )
            self.connection.commit()
        
            messagebox.showinfo("Success", "Prescription updated successfully")
            dialog.destroy()
            self.search_prescription()  # Refresh the view
            self.update_status(f"Updated prescription #{self.current_prescription_id}")
        
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
        except Exception as e:
            self.connection.rollback()
            messagebox.showerror("Error", f"Failed to update prescription: {str(e)}")
    
    def setup_search_tab(self):
        # Main container with padding
        search_container = ttk.Frame(self.search_tab)
        search_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Search options card
        options_frame = ttk.LabelFrame(
            search_container, 
            text=" 🔎 Search Options ",
            style='Card.TLabelframe'
        )
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Date search
        date_frame = ttk.Frame(options_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="📅 Search by Date:").pack(side=tk.LEFT)
        self.search_date_entry = ttk.Entry(date_frame, width=15, font=("Helvetica", 10))
        self.search_date_entry.pack(side=tk.LEFT, padx=5)
        self.search_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(
            date_frame, 
            text="Search", 
            command=self.search_by_date,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        # Amount range search
        amount_frame = ttk.Frame(options_frame)
        amount_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(amount_frame, text="💰 Search by Amount Range:").pack(side=tk.LEFT)
        
        ttk.Label(amount_frame, text="From:").pack(side=tk.LEFT, padx=(10, 0))
        self.min_amount_entry = ttk.Entry(amount_frame, width=10, font=("Helvetica", 10))
        self.min_amount_entry.pack(side=tk.LEFT)
        
        ttk.Label(amount_frame, text="To:").pack(side=tk.LEFT, padx=(5, 0))
        self.max_amount_entry = ttk.Entry(amount_frame, width=10, font=("Helvetica", 10))
        self.max_amount_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            amount_frame, 
            text="Search", 
            command=self.search_by_amount,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        # Results card
        results_frame = ttk.LabelFrame(
            search_container, 
            text=" 📊 Search Results ",
            style='Card.TLabelframe'
        )
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results treeview with modern styling
        self.search_tree = ttk.Treeview(
            results_frame, 
            columns=('id', 'date', 'total'), 
            show='headings',
            style='Custom.Treeview'
        )
        
        # Configure columns
        self.search_tree.heading('id', text='Prescription ID', anchor=tk.CENTER)
        self.search_tree.heading('date', text='Date', anchor=tk.CENTER)
        self.search_tree.heading('total', text='Total Amount', anchor=tk.E)
        
        self.search_tree.column('id', width=120, anchor=tk.CENTER)
        self.search_tree.column('date', width=150, anchor=tk.CENTER)
        self.search_tree.column('total', width=150, anchor=tk.E)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            results_frame, 
            orient=tk.VERTICAL, 
            command=self.search_tree.yview
        )
        self.search_tree.configure(yscroll=scrollbar.set)
        
        # Grid layout
        self.search_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Configure grid weights
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Double click to view prescription
        self.search_tree.bind("<Double-1>", self.view_selected_prescription)
    
    # ========== DATABASE OPERATIONS ==========
    def execute_query(self, query, params=None, fetch=False):
        """Execute a database query and return results if needed"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                cursor.close()
                return True
                
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            return None
    
    def get_medicine_details(self, medicine_id):
        """Get medicine details from database"""
        query = """
        SELECT name, manufacturer, price, category, description, dosage, requires_prescription 
        FROM MEDICINES 
        WHERE medicine_id = %s
        """
        return self.execute_query(query, (medicine_id,), fetch=True)
    
    def get_prescription_details(self, prescription_id):
        """Get complete prescription details from database"""
        # Get prescription header
        query = "SELECT * FROM PRESCRIPTIONS WHERE prescription_id = %s"
        prescription = self.execute_query(query, (prescription_id,), fetch=True)
        
        if not prescription:
            return None
            
        # Get prescription medicines
        query = """
        SELECT m.medicine_id, m.name, m.manufacturer, m.price, 
               pm.quantity_bought, pm.total_price
        FROM PRESCRIPTION_MEDICINES pm
        JOIN MEDICINES m ON pm.medicine_id = m.medicine_id
        WHERE pm.prescription_id = %s
        """
        medicines = self.execute_query(query, (prescription_id,), fetch=True)
        
        prescription[0]['medicines'] = medicines
        return prescription[0]
    
    # ========== CREATE TAB FUNCTIONS ==========
    def add_medicine(self):
        """Add a medicine to the current prescription"""
        name = simpledialog.askstring("Add Medicine", "Enter medicine name:")
        if not name:
            return
            
        try:
            # Check if medicine exists
            medicine_id = Medicine.get_id_by_name(name)
            if not medicine_id:
                messagebox.showerror("Error", f"Medicine '{name}' not found")
                return
                
            # Check availability
            available = self.pm.check_medicine_availability(medicine_id)
            if not available:
                messagebox.showerror("Error", f"Medicine '{name}' is out of stock")
                return
                
            # Get quantity with validation
            qty = simpledialog.askinteger(
                "Add Medicine", 
                f"Enter quantity (Available: {available}):",
                minvalue=1,
                maxvalue=available
            )
            if not qty:
                return
                
            # Get medicine details
            medicine_details = self.get_medicine_details(medicine_id)
            if not medicine_details:
                messagebox.showerror("Error", "Could not retrieve medicine details")
                return
                
            price = medicine_details[0]['price']
            total = qty * price
            
            # Add to treeview
            self.meds_tree.insert('', tk.END, values=(
                name, 
                qty, 
                f"${price:.2f}", 
                f"${total:.2f}"
            ))
            
            self.update_total()
            self.update_status(f"Added {qty} of {name} to prescription")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine: {str(e)}")
    
    def remove_medicine(self):
        """Remove selected medicine from current prescription"""
        selected = self.meds_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine to remove")
            return
            
        for item in selected:
            self.meds_tree.delete(item)
        
        self.update_total()
        self.update_status("Removed selected medicine(s)")
    
    def update_total(self):
        """Calculate and update the total amount for the prescription"""
        total = 0.0
        for child in self.meds_tree.get_children():
            values = self.meds_tree.item(child, 'values')
            total += float(values[3][1:])  # Remove $ and convert to float
        self.total_var.set(f"${total:.2f}")
    
    def create_prescription(self):
        """Save the current prescription to database"""
        if not self.meds_tree.get_children():
            messagebox.showwarning("Warning", "Please add at least one medicine")
            return
            
        try:
            cursor = self.connection.cursor()
            
            # Create prescription header
            cursor.execute("SELECT COALESCE(MAX(prescription_id), 0) FROM PRESCRIPTIONS")
            max_id = cursor.fetchone()[0]
            prescription_id = max_id + 1            
            prescription_date = datetime.now().date()
            cursor.execute(
                "INSERT INTO PRESCRIPTIONS (prescription_id,date, total_amount) VALUES (%s,%s, 0.00)",
                (prescription_id,prescription_date,)
            )
            
            # Add each medicine to the prescription
            for child in self.meds_tree.get_children():
                values = self.meds_tree.item(child, 'values')
                medicine_name = values[0]
                quantity = int(values[1])
                price = float(values[2][1:])
                
                medicine_id = Medicine.get_id_by_name(medicine_name)
                if not medicine_id:
                    raise ValueError(f"Medicine '{medicine_name}' not found")
                
                # Add to prescription_medicines
                cursor.execute(
                    """INSERT INTO PRESCRIPTION_MEDICINES 
                    (prescription_id, medicine_id, quantity_bought, total_price)
                    VALUES (%s, %s, %s, %s)""",
                    (prescription_id, medicine_id, quantity, quantity * price)
                )
                
                # Update inventory
                self.pm.adjust_inventory_quantity(medicine_id, -quantity)
            
            # Calculate and update total amount
            cursor.execute(
                """UPDATE PRESCRIPTIONS 
                SET total_amount = (
                    SELECT SUM(total_price) 
                    FROM PRESCRIPTION_MEDICINES 
                    WHERE prescription_id = %s
                )
                WHERE prescription_id = %s""",
                (prescription_id, prescription_id)
            )
            
            self.connection.commit()
            messagebox.showinfo(
                "Success", 
                f"Prescription #{prescription_id} created successfully!"
            )
            self.clear_form()
            self.update_status(f"Created new prescription #{prescription_id}")
            
        except Exception as e:
            self.connection.rollback()
            messagebox.showerror("Error", f"Failed to create prescription: {str(e)}")
    
    def clear_form(self):
        """Clear the prescription creation form"""
        for child in self.meds_tree.get_children():
            self.meds_tree.delete(child)
        self.total_var.set("0.00")
    
    # ========== VIEW TAB FUNCTIONS ==========
    def search_prescription(self):
        """Search for a prescription by ID"""
        pres_id = self.search_id_entry.get()
        if not pres_id:
            messagebox.showwarning("Warning", "Please enter a prescription ID")
            return
            
        try:
            prescription = self.get_prescription_details(int(pres_id))
            if not prescription:
                messagebox.showwarning("Warning", f"Prescription #{pres_id} not found")
                return
                
            self.current_prescription_id = prescription['prescription_id']
            
            # Update display
            self.view_id_var.set(prescription['prescription_id'])
            self.view_date_var.set(prescription['date'])
            self.view_total_var.set(f"${prescription['total_amount']:.2f}")
            
            # Clear existing items
            for child in self.view_meds_tree.get_children():
                self.view_meds_tree.delete(child)
            
            # Add medicines to treeview
            for med in prescription['medicines']:
                self.view_meds_tree.insert('', tk.END, values=(
                    med['name'],
                    med['quantity_bought'],
                    f"${med['price']:.2f}",
                    f"${med['total_price']:.2f}"
                ))
            
            self.update_status(f"Loaded prescription #{pres_id}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid prescription ID")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load prescription: {str(e)}")
    

    
    def clear_view_form(self):
        """Clear the view prescription form"""
        self.current_prescription_id = None
        self.view_id_var.set("")
        self.view_date_var.set("")
        self.view_total_var.set("")
        for child in self.view_meds_tree.get_children():
            self.view_meds_tree.delete(child)
    
    # ========== SEARCH TAB FUNCTIONS ==========
    def search_by_date(self):
        """Search prescriptions by date"""
        date_str = self.search_date_entry.get()
        if not date_str:
            messagebox.showwarning("Warning", "Please enter a date")
            return
            
        try:
            # Validate date format
            datetime.strptime(date_str, "%Y-%m-%d")
            
            # Search prescriptions
            query = "SELECT * FROM PRESCRIPTIONS WHERE date = %s ORDER BY prescription_id"
            prescriptions = self.execute_query(query, (date_str,), fetch=True)
            
            if not prescriptions:
                messagebox.showinfo("Info", f"No prescriptions found for {date_str}")
                return
                
            self.display_search_results(prescriptions)
            self.update_status(f"Found {len(prescriptions)} prescriptions for {date_str}")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search prescriptions: {str(e)}")
    
    def search_by_amount(self):
        """Search prescriptions by amount range"""
        try:
            min_amt = float(self.min_amount_entry.get() or 0)
            max_amt = float(self.max_amount_entry.get() or float('inf'))
            
            if min_amt > max_amt:
                messagebox.showwarning("Warning", "Minimum amount cannot be greater than maximum")
                return
                
            # Search prescriptions
            query = """
            SELECT * FROM PRESCRIPTIONS 
            WHERE total_amount BETWEEN %s AND %s 
            ORDER BY total_amount
            """
            prescriptions = self.execute_query(query, (min_amt, max_amt), fetch=True)
            
            if not prescriptions:
                messagebox.showinfo(
                    "Info", 
                    f"No prescriptions found between ${min_amt:.2f} and ${max_amt:.2f}"
                )
                return
                
            self.display_search_results(prescriptions)
            self.update_status(
                f"Found {len(prescriptions)} prescriptions in range ${min_amt:.2f}-${max_amt:.2f}"
            )
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid amounts")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search prescriptions: {str(e)}")
    
    def display_search_results(self, prescriptions):
        """Display search results in the treeview"""
        # Clear existing items
        for child in self.search_tree.get_children():
            self.search_tree.delete(child)
        
        # Add new results
        for pres in prescriptions:
            self.search_tree.insert('', tk.END, values=(
                pres['prescription_id'],
                pres['date'],
                f"${pres['total_amount']:.2f}"
            ))
    
    def view_selected_prescription(self, event):
        """View a prescription selected from search results"""
        selected = self.search_tree.selection()
        if not selected:
            return
            
        pres_id = self.search_tree.item(selected[0], 'values')[0]
        
        # Switch to view tab and load the prescription
        self.notebook.select(self.view_tab)
        self.search_id_entry.delete(0, tk.END)
        self.search_id_entry.insert(0, pres_id)
        self.search_prescription()



    # def save_prescription_changes(self):
    #     """Save any changes made to the current prescription"""
    #     if not self.current_prescription_id:
    #         messagebox.showwarning("Warning", "No prescription loaded to save")
    #         return

    #     try:
    #         # Get all medicines from the treeview
    #         medicines = []
    #         for child in self.view_meds_tree.get_children():
    #             values = self.view_meds_tree.item(child, 'values')
    #             medicines.append({
    #             'name': values[0],
    #             'quantity': int(values[1]),
    #             'price': float(values[2][1:]),  # Remove $ sign
    #             'total': float(values[3][1:])
    #              })
    
    #         # Update prescription in database
    #         cursor = self.connection.cursor()
    
    #         # First clear existing prescription medicines
    #         cursor.execute(
    #         "DELETE FROM PRESCRIPTION_MEDICINES WHERE prescription_id = %s",
    #         (self.current_prescription_id,)
    #         )
    
    #         # Add updated medicines
    #         for med in medicines:
    #             medicine_id = Medicine.get_id_by_name(med['name'])
    #             if not medicine_id:
    #                 raise ValueError(f"Medicine '{med['name']}' not found")
        
    #         cursor.execute(
    #             """INSERT INTO PRESCRIPTION_MEDICINES 
    #             (prescription_id, medicine_id, quantity_bought, total_price)
    #             VALUES (%s, %s, %s, %s)""",
    #             (self.current_prescription_id, medicine_id, med['quantity'], med['total'])
    #         )
    
    #         # Update total amount
    #         cursor.execute(
    #         """UPDATE PRESCRIPTIONS 
    #         SET total_amount = (
    #             SELECT SUM(total_price) 
    #             FROM PRESCRIPTION_MEDICINES 
    #             WHERE prescription_id = %s
    #         )
    #         WHERE prescription_id = %s""",
    #         (self.current_prescription_id, self.current_prescription_id)
    #         )
    
    #         self.connection.commit()
    #         messagebox.showinfo("Success", "Prescription changes saved successfully")
    #         self.update_status(f"Saved changes to prescription #{self.current_prescription_id}")
    
    #     except Exception as e:
    #         self.connection.rollback()
    #         messagebox.showerror("Error", f"Failed to save changes: {str(e)}")


    def add_medicine_to_existing(self):

        """Add a medicine to an existing prescription"""
        if not self.current_prescription_id:
            messagebox.showwarning("Warning", "Please search for a prescription first")
            return
        
        name = simpledialog.askstring("Add Medicine", "Enter medicine name:")
        if not name:
            return
        
        try:
            medicine_id = Medicine.get_id_by_name(name)
            if not medicine_id:
                messagebox.showerror("Error", f"Medicine '{name}' not found")
                return
            
            available = self.pm.check_medicine_availability(medicine_id)
            if not available:
                messagebox.showerror("Error", f"Medicine '{name}' is out of stock")
                return
            
            qty = simpledialog.askinteger(
            "Add Medicine", 
            f"Enter quantity (Available: {available}):",
            minvalue=1,
            maxvalue=available
            )
            if not qty:
                return
            
            # Add to prescription using the existing connection
            cursor = self.connection.cursor()
            self.pm._add_medicine_to_prescription(cursor, self.current_prescription_id, medicine_id, qty)
            self.connection.commit()
        
            # Refresh the view
            self.search_prescription()
            self.update_status(f"Added {name} to prescription #{self.current_prescription_id}")
        
        except Exception as e:
            self.connection.rollback()
            messagebox.showerror("Error", f"Failed to add medicine: {str(e)}")


    def remove_medicine_from_existing(self):
        """Remove a medicine from an existing prescription"""
        selected = self.view_meds_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine to remove")
            return
        
        if not self.current_prescription_id:
            messagebox.showwarning("Warning", "Please search for a prescription first")
            return
        
        try:
            medicine_name = self.view_meds_tree.item(selected[0], 'values')[0]
            medicine_id = Medicine.get_id_by_name(medicine_name)
        
            if messagebox.askyesno(
            "Confirm Removal",
            f"Remove {medicine_name} from prescription #{self.current_prescription_id}?"
            ):
                cursor = self.connection.cursor()
                self.pm.remove_medicine_from_prescription(self.current_prescription_id, medicine_id)
                self.connection.commit()
                self.search_prescription()  # Refresh view
                self.update_status(f"Removed {medicine_name} from prescription")
            
        except Exception as e:
            self.connection.rollback()
            messagebox.showerror("Error", f"Failed to remove medicine: {str(e)}")



    def update_medicine_quantity(self):
        """Update the quantity of a medicine in an existing prescription"""
        selected = self.view_meds_tree.selection()
        if not selected or len(selected) > 1:
            messagebox.showwarning("Warning", "Please select one medicine to update")
            return
        
        if not self.current_prescription_id:
            messagebox.showwarning("Warning", "Please search for a prescription first")
            return
        
        try:
            values = self.view_meds_tree.item(selected[0], 'values')
            medicine_name = values[0]
            current_qty = int(values[1])
            medicine_id = Medicine.get_id_by_name(medicine_name)
        
            # Get available stock (current stock + quantity in prescription)
            available = self.pm.check_medicine_availability(medicine_id) + current_qty
        
            new_qty = simpledialog.askinteger(
            "Update Quantity", 
            f"Current: {current_qty}\nAvailable: {available}\nEnter new quantity:",
            minvalue=1,
            maxvalue=available
            )
        
            if new_qty and new_qty != current_qty:
                cursor = self.connection.cursor()
                self.pm.update_prescription_medicine(
                
                self.current_prescription_id, 
                medicine_id, 
                new_qty
            )
            self.connection.commit()
            self.search_prescription()  # Refresh view
            self.update_status(f"Updated quantity for {medicine_name}")
            
        except Exception as e:
            self.connection.rollback()
            messagebox.showerror("Error", f"Failed to update quantity: {str(e)}")


    def delete_prescription(self):
        """Delete the current prescription"""
        if not self.current_prescription_id:
            messagebox.showwarning("Warning", "Please search for a prescription first")
            return
        
        if messagebox.askyesno(
            "Confirm Deletion", 
            f"Delete prescription #{self.current_prescription_id}? This cannot be undone.",
            icon='warning'
        ):
            try:
                cursor = self.connection.cursor()
                self.pm.delete_prescription(self.current_prescription_id)
                self.connection.commit()
                messagebox.showinfo("Success", "Prescription deleted successfully")
                self.clear_view_form()
                self.update_status(f"Deleted prescription #{self.current_prescription_id}")
            
            except Exception as e:
                self.connection.rollback()
                messagebox.showerror("Error", f"Failed to delete prescription: {str(e)}")
























            

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    
    # Set window icon
    try:
        root.iconbitmap('pharmacy.ico')
    except:
        pass
    
    app = PrescriptionGUI(root)
    root.mainloop()