from tkinter import *
import customtkinter
from tkinter import messagebox

# Main Window Properties
window = Tk()
window.title("PMS-Register")
window.geometry("1000x350")
window.configure(bg="#FFFFFF")


from users import UserManager

# Assuming you have a connection and cursor setup for database
cursor = None  # Replace with actual database cursor
conn = None  # Replace with actual database connection
user_manager = UserManager(cursor, conn)

# Entry Fields for Name, Email, Phone, Password, etc.
Entry_id9 = customtkinter.CTkEntry(master=window, placeholder_text="Muhammad Saad Zubair", placeholder_text_color="#454545", font=("Arial", 14), text_color="#000000", height=31, width=195, border_width=2, corner_radius=6, border_color="#000000", bg_color="#FFFFFF", fg_color="#F0F0F0")
Entry_id9.place(x=180, y=140)

Entry_id11 = customtkinter.CTkEntry(master=window, placeholder_text="saad@gmail.com", placeholder_text_color="#454545", font=("Arial", 14), text_color="#000000", height=30, width=197, border_width=2, corner_radius=6, border_color="#000000", bg_color="#FFFFFF", fg_color="#F0F0F0")
Entry_id11.place(x=180, y=190)

Entry_id10 = customtkinter.CTkEntry(master=window, placeholder_text="+92 312-4351262", placeholder_text_color="#454545", font=("Arial", 14), text_color="#000000", height=31, width=195, border_width=2, corner_radius=6, border_color="#000000", bg_color="#FFFFFF", fg_color="#F0F0F0")
Entry_id10.place(x=180, y=240)

Entry_id14 = customtkinter.CTkEntry(master=window, placeholder_text="Password", placeholder_text_color="#454545", font=("Arial", 14), text_color="#000000", height=31, width=195, border_width=2, corner_radius=6, border_color="#000000", bg_color="#FFFFFF", fg_color="#F0F0F0")
Entry_id14.place(x=650, y=190)

Entry_id13 = customtkinter.CTkEntry(master=window, placeholder_text="Confirmed Password", placeholder_text_color="#454545", font=("Arial", 14), text_color="#000000", height=31, width=195, border_width=2, corner_radius=6, border_color="#000000", bg_color="#FFFFFF", fg_color="#F0F0F0")
Entry_id13.place(x=650, y=240)

radio_var = IntVar()
RadioButton_id20 = customtkinter.CTkRadioButton(master=window, variable=radio_var, value=20, text="Admin", text_color="#000000", border_color="#000000", fg_color="#808080", hover_color="#2F2F2F")
RadioButton_id20.place(x=650, y=140)

RadioButton_id21 = customtkinter.CTkRadioButton(master=window, variable=radio_var, value=21, text="Pharmacist", text_color="#000000", border_color="#000000", fg_color="#808080", hover_color="#2F2F2F")
RadioButton_id21.place(x=760, y=140)

# Label to display registration result
message_label = customtkinter.CTkLabel(master=window, text="", font=("Georgia", 15), text_color="#000000", height=30, width=400, corner_radius=0, bg_color="#FFFFFF", fg_color="#FFFFFF")
message_label.place(x=350, y=300)

# Function to handle registration
def handle_registration():
    name = Entry_id9.get()
    email = Entry_id11.get()
    phone = Entry_id10.get()
    password = Entry_id14.get()
    confirm_password = Entry_id13.get()
    role = "Admin" if radio_var.get() == 20 else "Pharmacist"

    # Check if passwords match
    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match!")
        return

    result = user_manager.register_user(name, email, phone, role, password)

    if result["success"]:
        message_label.configure(text=result["message"], text_color="green")
    else:
        message_label.configure(text=result["message"], text_color="red")

# Register Button
register_button = customtkinter.CTkButton(master=window, text="Register", command=handle_registration, width=200, height=40)
register_button.place(x=400, y=270)

# Run the main loop
window.mainloop()