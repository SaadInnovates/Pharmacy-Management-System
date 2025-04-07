# main_app.py
import customtkinter as ctk
from tkinter import messagebox
from theme import setup_theme
from login_gui import LoginWindow
from inventory_gui import InventoryWindow
from medicines_gui import MedicinesWindow
from suppliers_ui import SupplierGUI
from users_gui import UserManagerGUI
from prescriptions_gui import PrescriptionGUI
from predictor_ui import MedicinePredictorGUI
import tkinter as tk

class MainApplication:
    def __init__(self):
        self.theme = setup_theme()
        self.current_user = None
        self.current_user_role = None
        from users import UserManager
        self.user_manager = UserManager()  # Make it an instance attribute!
        
        # First show login window
        self.show_login()
    
    def show_login(self):
        """Show login window"""
        from users import UserManager

        login_window = LoginWindow(self.user_manager)
        login_window.window.mainloop()
        
        # After login, check if authentication was successful
        # Note: This is a simplified approach - in a real app you'd have proper callbacks
       
        self.current_user = self.user_manager.get_current_user()  # You'll need to implement this in your UserManager
        if self.current_user:
            self.current_user_role = self.current_user.get('role', 'Pharmacist')
            self.show_main_menu()
        
    
    def show_main_menu(self):
        """Show main menu based on user role"""
        self.root = ctk.CTk()
        self.root.title("Pharmacy Management System")
        self.root.geometry("1000x700")
        
        # Configure theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color=self.theme["bg_color"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Pharmacy Management System",
            font=self.theme["font_title"],
            text_color=self.theme["primary_color"]
        )
        title_label.pack(side="left", padx=10)
        
        user_label = ctk.CTkLabel(
            header_frame,
            text=f"Logged in as: {self.current_user.get('name', 'User')} ({self.current_user_role})",
            font=self.theme["font_body"],
            text_color=self.theme["text_secondary"]
        )
        user_label.pack(side="right", padx=10)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        nav_frame.pack(fill="x", pady=10)
        
        # Button style
        button_style = {
            "width": 200,
            "height": 50,
            "font": self.theme["font_button"],
            "corner_radius": 8,
            "fg_color": self.theme["primary_color"],
            "hover_color": self.theme["secondary_color"]
        }
        
        # Inventory Management
        inventory_btn = ctk.CTkButton(
            nav_frame,
            text="📦 Inventory Management",
            command=self.open_inventory,
            **button_style
        )
        inventory_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # Medicines Management
        medicines_btn = ctk.CTkButton(
            nav_frame,
            text="💊 Medicines Management",
            command=self.open_medicines,
            **button_style
        )
        medicines_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Suppliers Management
        suppliers_btn = ctk.CTkButton(
            nav_frame,
            text="🏢 Suppliers Management",
            command=self.open_suppliers,
            **button_style
        )
        suppliers_btn.grid(row=1, column=0, padx=10, pady=10)
        
        # Prescriptions Management
        prescriptions_btn = ctk.CTkButton(
            nav_frame,
            text="📝 Prescriptions Management",
            command=self.open_prescriptions,
            **button_style
        )
        prescriptions_btn.grid(row=1, column=1, padx=10, pady=10)
        
        # Medicine Effectiveness Prediction
        predictor_btn = ctk.CTkButton(
            nav_frame,
            text="🔮 Effectiveness Predictor",
            command=self.open_predictor,
            **button_style
        )
        predictor_btn.grid(row=2, column=0, padx=10, pady=10)
        
        # Users Management (only for admin)
        if self.current_user_role == "Admin":
            users_btn = ctk.CTkButton(
                nav_frame,
                text="👥 Users Management",
                command=self.open_users,
                **button_style
            )
            users_btn.grid(row=2, column=1, padx=10, pady=10)
        
        # Logout button
        logout_btn = ctk.CTkButton(
            nav_frame,
            text="🚪 Logout",
            command=self.logout,
            width=200,
            height=40,
            fg_color=self.theme["error_color"],
            hover_color="#c82333",
            font=self.theme["font_button"],
            corner_radius=8
        )
        logout_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Configure grid
        nav_frame.grid_columnconfigure(0, weight=1)
        nav_frame.grid_columnconfigure(1, weight=1)
        
        self.root.mainloop()
    
    def open_inventory(self):
        """Open inventory management window"""
        self.root.withdraw()  # Hide main menu
        inventory_window = InventoryWindow()
        inventory_window.window.protocol("WM_DELETE_WINDOW", lambda: self.on_child_close(inventory_window.window))
        inventory_window.run()
    
    def open_medicines(self):
        """Open medicines management window"""
        self.root.withdraw()
        medicines_window = MedicinesWindow()
        medicines_window.window.protocol("WM_DELETE_WINDOW", lambda: self.on_child_close(medicines_window.window))
        medicines_window.run()
    
    def open_suppliers(self):
        """Open suppliers management window"""
        self.root.withdraw()
        supplier_window = ctk.CTk()
        supplier_gui = SupplierGUI(supplier_window)
        supplier_window.protocol("WM_DELETE_WINDOW", lambda: self.on_child_close(supplier_window))
        supplier_window.mainloop()
    
    def open_users(self):
        """Open users management window (admin only)"""
        if self.current_user_role == "Admin":
            self.root.withdraw()

            users_window = tk.Toplevel()
            users_gui = UserManagerGUI(users_window, self.user_manager, self.current_user_role, self.current_user)
            users_window.protocol("WM_DELETE_WINDOW", lambda: self.on_child_close(users_window))
            users_window.mainloop()
    
    def open_prescriptions(self):
        """Open prescriptions management window"""
        self.root.withdraw()
        prescriptions_window = ctk.CTkToplevel()
        prescriptions_gui = PrescriptionGUI(prescriptions_window)
        prescriptions_window.protocol("WM_DELETE_WINDOW", lambda: self.on_child_close(prescriptions_window))
        prescriptions_window.mainloop()
    
    def open_predictor(self):
        """Open medicine effectiveness predictor"""
        self.root.withdraw()
        predictor_window = ctk.CTkToplevel()
        predictor_gui = MedicinePredictorGUI(predictor_window)
        predictor_window.protocol("WM_DELETE_WINDOW", lambda: self.on_child_close(predictor_window))
        predictor_window.mainloop()
    
    def on_child_close(self, child_window):
        """Handle child window closing"""
        child_window.destroy()
        self.root.deiconify()  # Show main menu again
    
    def logout(self):
        """Logout current user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.current_user_role = None
            self.root.destroy()
            self.show_login()

if __name__ == "__main__":
    app = MainApplication()