# login_gui.py
import customtkinter
from tkinter import messagebox
from theme import setup_theme
from users import UserManager

class LoginWindow:
    def __init__(self,user_manager):
        self.user_manager = user_manager
        self.theme = setup_theme()
        
        self.window = customtkinter.CTk()
        self.window.title("Pharmacy Management - Login")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = customtkinter.CTkFrame(self.window, fg_color=self.theme["bg_color"])
        main_frame.pack(pady=40, padx=40, fill="both", expand=True)
        
        # Title
        title_label = customtkinter.CTkLabel(
            main_frame, 
            text="Pharmacy Management",
            font=self.theme["font_title"],
            text_color=self.theme["primary_color"]
        )
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = customtkinter.CTkLabel(
            main_frame,
            text="Secure Login Portal",
            font=self.theme["font_subtitle"],
            text_color=self.theme["text_secondary"]
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Login form frame
        form_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20)
        
        # Email field
        email_label = customtkinter.CTkLabel(
            form_frame,
            text="Email Address",
            font=self.theme["font_body"],
            anchor="w"
        )
        email_label.pack(fill="x", pady=(5, 0))
        
        self.email_entry = customtkinter.CTkEntry(
            form_frame,
            placeholder_text="your@email.com",
            width=300,
            height=40,
            font=self.theme["font_body"],
            corner_radius=8,
            fg_color=self.theme["entry_bg"],
            border_color=self.theme["entry_border"]
        )
        self.email_entry.pack(pady=(0, 15))
        
        # Password field
        password_label = customtkinter.CTkLabel(
            form_frame,
            text="Password",
            font=self.theme["font_body"],
            anchor="w"
        )
        password_label.pack(fill="x", pady=(5, 0))
        
        self.password_entry = customtkinter.CTkEntry(
            form_frame,
            placeholder_text="••••••••",
            width=300,
            height=40,
            font=self.theme["font_body"],
            corner_radius=8,
            fg_color=self.theme["entry_bg"],
            border_color=self.theme["entry_border"],
            show="•"
        )
        self.password_entry.pack(pady=(0, 20))
        
        # Remember me checkbox
        self.remember_me = customtkinter.CTkCheckBox(
            form_frame,
            text="Remember me",
            font=self.theme["font_body"]
        )
        self.remember_me.pack(pady=(0, 20))
        
        # Login button
        login_button = customtkinter.CTkButton(
            form_frame,
            text="Login",
            width=300,
            height=40,
            font=self.theme["font_button"],
            corner_radius=8,
            fg_color=self.theme["primary_color"],
            hover_color=self.theme["secondary_color"],
            command=self.attempt_login
        )
        login_button.pack(pady=(0, 10))
        
        # Forgot password
        forgot_password = customtkinter.CTkLabel(
            form_frame,
            text="Forgot password?",
            font=self.theme["font_body"],
            text_color=self.theme["primary_color"],
            cursor="hand2"
        )
        forgot_password.pack()
        forgot_password.bind("<Button-1>", lambda e: self.on_forgot_password())
        
        # Footer
        footer = customtkinter.CTkLabel(
            main_frame,
            text="© 2023 Pharmacy Management System",
            font=("Roboto", 10),
            text_color=self.theme["text_secondary"]
        )
        footer.pack(pady=(30, 0))
        
    def attempt_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            self.show_error("Please enter both email and password")
            return
        
        result = self.user_manager.authenticate_user(email, password)
        
        if result["success"]:
            # Set current user in UserManager
            self.user_manager.set_current_user(result["user"])
            messagebox.showinfo("Success", "Login successful!")
            self.window.destroy()
        else:
            self.show_error(result["message"])
    
    def on_forgot_password(self):
        messagebox.showinfo(
            "Password Recovery",
            "Please contact your system administrator\nadmin@pharmacy.com"
        )
    
    def show_error(self, message):
        error_label = customtkinter.CTkLabel(
            self.window,
            text=message,
            font=self.theme["font_body"],
            text_color=self.theme["error_color"]
        )
        error_label.place(relx=0.5, rely=0.9, anchor="center")
        self.window.after(3000, error_label.destroy)
    
    def run(self):
        self.window.mainloop()

# if __name__ == "__main__":
#     app = LoginWindow()
#     app.run()