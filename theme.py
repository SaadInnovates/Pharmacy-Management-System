# theme.py
import customtkinter

def setup_theme():
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("blue")
    
    return {
        "font_title": ("Roboto Medium", 24),
        "font_subtitle": ("Roboto", 14),
        "font_body": ("Roboto", 12),
        "font_button": ("Roboto Medium", 14),
        "primary_color": "#4B89DC",
        "secondary_color": "#50C878",
        "error_color": "#FF6B6B",
        "warning_color": "#FFA500",
        "text_primary": "#2B2B2B",
        "text_secondary": "#5A5A5A",
        "bg_color": "#FFFFFF",
        "entry_bg": "#FAFAFA",
        "entry_border": "#E0E0E0"
    }