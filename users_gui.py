import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk

class UserManagerGUI:
    def __init__(self, root, user_manager, current_user_role, current_user):
        self.root = root
        self.user_manager = user_manager
        self.current_user_role = current_user_role
        self.current_user = current_user
        
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("Pharmacy Management System - User Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f8ff')
        
        # Custom style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('TFrame', background='#f0f8ff')
        style.configure('TLabel', background='#f0f8ff', font=('Helvetica', 10))
        style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'), foreground='#2c3e50')
        style.configure('TButton', font=('Helvetica', 10), padding=5)
        style.configure('Primary.TButton', foreground='white', background='#3498db')
        style.configure('Secondary.TButton', foreground='white', background='#2ecc71')
        style.configure('Danger.TButton', foreground='white', background='#e74c3c')
        style.configure('TEntry', padding=5)
        style.configure('TCombobox', padding=5)
        
        # Header frame
        header_frame = ttk.Frame(self.root, style='TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add a logo (placeholder)
        try:
            logo_img = Image.open("pharmacy_logo.png").resize((50, 50))
            self.logo = ImageTk.PhotoImage(logo_img)
            logo_label = ttk.Label(header_frame, image=self.logo)
            logo_label.grid(row=0, column=0, padx=(0, 10))
        except:
            pass
        
        ttk.Label(
            header_frame, 
            text="USER MANAGEMENT", 
            style='Header.TLabel'
        ).grid(row=0, column=1, sticky='w')
        
        # Current user info
        user_info = f"Logged in as: {self.current_user.get('name', '')} ({self.current_user_role})"
        ttk.Label(
            header_frame, 
            text=user_info,
            font=('Helvetica', 10, 'italic')
        ).grid(row=0, column=2, sticky='e', padx=10)
        
        # Main content frame
        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Button frame
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create buttons for each action
        buttons = [
            ("Register New User", self.register_user, 'Secondary.TButton'),
            ("Update User", self.update_user, 'Primary.TButton'),
            ("View User Details", self.view_user, 'Primary.TButton'),
            ("List All Users", self.list_users, 'Primary.TButton'),
            ("Reset Password", self.reset_password, 'Secondary.TButton'),
            ("Delete User", self.delete_user, 'Danger.TButton'),
            ("Exit", self.exit_app, 'Danger.TButton')
        ]
        
        for i, (text, command, style_name) in enumerate(buttons):
            btn = ttk.Button(
                button_frame,
                text=text,
                command=command,
                style=style_name,
                width=15
            )
            btn.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
            button_frame.columnconfigure(i, weight=1)
        
        # Output area
        self.output_area = ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Consolas', 10),
            bg='white',
            fg='black'
        )
        self.output_area.pack(fill=tk.BOTH, expand=True)
        self.output_area.configure(state='disabled')
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=('Helvetica', 9)
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)
    
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def clear_output(self):
        self.output_area.configure(state='normal')
        self.output_area.delete(1.0, tk.END)
        self.output_area.configure(state='disabled')
    
    def append_output(self, text):
        self.output_area.configure(state='normal')
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.configure(state='disabled')
        self.output_area.see(tk.END)
    
    def register_user(self):
        if self.current_user_role != "Admin":
            messagebox.showerror("Permission Denied", "Only Admins can register new users!")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Register New User")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Full Name:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        
        ttk.Label(dialog, text="Email:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        email_entry = ttk.Entry(dialog, width=30)
        email_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        
        ttk.Label(dialog, text="Phone:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        phone_entry = ttk.Entry(dialog, width=30)
        phone_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        
        ttk.Label(dialog, text="Role:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        role_var = tk.StringVar()
        role_combobox = ttk.Combobox(dialog, textvariable=role_var, values=["Admin", "Pharmacist"], state='readonly')
        role_combobox.grid(row=3, column=1, padx=10, pady=5, sticky='w')
        
        ttk.Label(dialog, text="Password:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        password_entry = ttk.Entry(dialog, width=30, show="*")
        password_entry.grid(row=4, column=1, padx=10, pady=5, sticky='w')
        
        ttk.Label(dialog, text="Confirm Password:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
        confirm_entry = ttk.Entry(dialog, width=30, show="*")
        confirm_entry.grid(row=5, column=1, padx=10, pady=5, sticky='w')
        
        def submit():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()
            role = role_var.get()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords don't match!")
                return
                
            result = self.user_manager.register_user(name, email, phone, role, password)
            messagebox.showinfo("Result", result["message"])
            if result["success"]:
                dialog.destroy()
        
        submit_btn = ttk.Button(dialog, text="Register", command=submit, style='Secondary.TButton')
        submit_btn.grid(row=6, column=1, padx=10, pady=10, sticky='e')
        
        cancel_btn = ttk.Button(dialog, text="Cancel", command=dialog.destroy, style='Danger.TButton')
        cancel_btn.grid(row=6, column=0, padx=10, pady=10, sticky='w')
    
    def update_user(self):
        try:
            user_id = simpledialog.askinteger("Update User", "Enter User ID to update:")
            if user_id is None:
                return
                
            # Get current user info
            result = self.user_manager.get_user_by_id(user_id)
            if not result["success"]:
                messagebox.showerror("Error", result["message"])
                return
                
            current_user = result["user"]
            
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Update User {user_id}")
            dialog.geometry("500x500")
            dialog.resizable(False, False)
            dialog.grab_set()
            
            # Current values label
            current_values = "\n".join([f"{k}: {v}" for k, v in current_user.items()])
            ttk.Label(dialog, text="Current Values:").grid(row=0, column=0, padx=10, pady=5, sticky='ne')
            ttk.Label(dialog, text=current_values).grid(row=0, column=1, padx=10, pady=5, sticky='nw')
            
            ttk.Label(dialog, text="\nLeave fields blank to keep current values\n", 
                     font=('Helvetica', 9, 'italic')).grid(row=1, column=0, columnspan=2, pady=5)
            
            ttk.Label(dialog, text="New Name:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
            name_entry = ttk.Entry(dialog, width=30)
            name_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
            
            ttk.Label(dialog, text="New Email:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
            email_entry = ttk.Entry(dialog, width=30)
            email_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')
            
            ttk.Label(dialog, text="New Phone:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
            phone_entry = ttk.Entry(dialog, width=30)
            phone_entry.grid(row=4, column=1, padx=10, pady=5, sticky='w')
            
            ttk.Label(dialog, text="New Role:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
            role_var = tk.StringVar()
            role_combobox = ttk.Combobox(dialog, textvariable=role_var, values=["Admin", "Pharmacist"], state='readonly')
            role_combobox.grid(row=5, column=1, padx=10, pady=5, sticky='w')
            
            # Only show password fields if admin or updating own account
            change_pass = False
            if self.current_user_role == "Admin" or user_id == self.current_user.get("user_id"):
                change_pass_var = tk.BooleanVar(value=False)
                pass_check = ttk.Checkbutton(
                    dialog, 
                    text="Change Password", 
                    variable=change_pass_var,
                    command=lambda: toggle_pass_entries(change_pass_var.get())
                )
                pass_check.grid(row=6, column=0, columnspan=2, pady=5)
                
                ttk.Label(dialog, text="New Password:").grid(row=7, column=0, padx=10, pady=5, sticky='e')
                password_entry = ttk.Entry(dialog, width=30, show="*")
                password_entry.grid(row=7, column=1, padx=10, pady=5, sticky='w')
                password_entry.grid_remove()
                
                ttk.Label(dialog, text="Confirm Password:").grid(row=8, column=0, padx=10, pady=5, sticky='e')
                confirm_entry = ttk.Entry(dialog, width=30, show="*")
                confirm_entry.grid(row=8, column=1, padx=10, pady=5, sticky='w')
                confirm_entry.grid_remove()
                
                def toggle_pass_entries(show):
                    if show:
                        password_entry.grid()
                        confirm_entry.grid()
                    else:
                        password_entry.grid_remove()
                        confirm_entry.grid_remove()
            
            def submit():
                name = name_entry.get().strip() or None
                email = email_entry.get().strip() or None
                phone = phone_entry.get().strip() or None
                role = role_var.get() or None
                
                password = None
                if 'change_pass_var' in locals() and change_pass_var.get():
                    password = password_entry.get()
                    confirm = confirm_entry.get()
                    
                    if password != confirm:
                        messagebox.showerror("Error", "Passwords don't match!")
                        return
                
                result = self.user_manager.update_user(
                    user_id, name, email, phone, role, password
                )
                messagebox.showinfo("Result", result["message"])
                if result["success"]:
                    dialog.destroy()
            
            submit_btn = ttk.Button(dialog, text="Update", command=submit, style='Primary.TButton')
            submit_btn.grid(row=9, column=1, padx=10, pady=10, sticky='e')
            
            cancel_btn = ttk.Button(dialog, text="Cancel", command=dialog.destroy, style='Danger.TButton')
            cancel_btn.grid(row=9, column=0, padx=10, pady=10, sticky='w')
            
        except ValueError:
            messagebox.showerror("Error", "Invalid ID. Please enter a number.")
    
    def view_user(self):
        try:
            user_id = simpledialog.askinteger("View User", "Enter User ID:")
            if user_id is None:
                return
                
            result = self.user_manager.get_user_by_id(user_id)
            self.clear_output()
            
            if result["success"]:
                self.append_output("User Details:")
                for k, v in result["user"].items():
                    self.append_output(f"{k:>15}: {v}")
            else:
                self.append_output(result["message"])
                
        except ValueError:
            messagebox.showerror("Error", "Invalid ID. Please enter a number.")
    
    def list_users(self):
        if self.current_user_role != "Admin":
            messagebox.showerror("Permission Denied", "Only Admins can view all users!")
            return
            
        role_filter = None
        if messagebox.askyesno("Filter", "Filter by role?"):
            role = simpledialog.askstring("Filter", "Enter role (Admin/Pharmacist):")
            if role and role.capitalize() in ["Admin", "Pharmacist"]:
                role_filter = role.capitalize()
        
        users = self.user_manager.get_all_users(role_filter)
        self.clear_output()
        
        if isinstance(users, list):
            self.append_output(f"{'ID':<5}{'Name':<30}{'Role':<15}{'Email':<30}")
            self.append_output("-" * 80)
            for user in users:
                self.append_output(f"{user['user_id']:<5}{user['name']:<30}{user['role']:<15}{user['email']:<30}")
        else:
            self.append_output(users.get("error", "Error fetching users"))
    
    def reset_password(self):
        if self.current_user_role != "Admin":
            messagebox.showerror("Permission Denied", "Only Admins can reset passwords!")
            return
            
        email = simpledialog.askstring("Reset Password", "Enter user email:")
        if not email:
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Reset Password")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        ttk.Label(dialog, text="New Password:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        new_pass_entry = ttk.Entry(dialog, width=30, show="*")
        new_pass_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        
        ttk.Label(dialog, text="Confirm Password:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        confirm_entry = ttk.Entry(dialog, width=30, show="*")
        confirm_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        
        def submit():
            new_pass = new_pass_entry.get()
            confirm = confirm_entry.get()
            
            if new_pass != confirm:
                messagebox.showerror("Error", "Passwords don't match!")
                return
                
            result = self.user_manager.reset_password(email, new_pass)
            messagebox.showinfo("Result", result["message"])
            if result["success"]:
                dialog.destroy()
        
        submit_btn = ttk.Button(dialog, text="Reset", command=submit, style='Secondary.TButton')
        submit_btn.grid(row=2, column=1, padx=10, pady=10, sticky='e')
        
        cancel_btn = ttk.Button(dialog, text="Cancel", command=dialog.destroy, style='Danger.TButton')
        cancel_btn.grid(row=2, column=0, padx=10, pady=10, sticky='w')
    
    def delete_user(self):
        if self.current_user_role != "Admin":
            messagebox.showerror("Permission Denied", "Only Admins can delete users!")
            return
            
        try:
            user_id = simpledialog.askinteger("Delete User", "Enter User ID to delete:")
            if user_id is None:
                return
                
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete user {user_id}? This cannot be undone!"):
                result = self.user_manager.delete_user(user_id)
                messagebox.showinfo("Result", result["message"])
                
        except ValueError:
            messagebox.showerror("Error", "Invalid ID. Please enter a number.")
    
    def exit_app(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.quit()


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    
    from users import UserManager
    # Create an instance of your actual UserManager
    user_manager = UserManager()
    
    # Example current user (replace with your actual authentication)
    current_user = {"user_id": 1, "name": "Admin User"}
    current_user_role = "Admin"
    
    app = UserManagerGUI(root, user_manager, current_user_role, current_user)
    root.mainloop()