import customtkinter as ctk
from tkinter import messagebox
from predictor import MedicineEffectivenessPredictor
from medicines import Medicine
from theme import setup_theme

class MedicinePredictorGUI:
    def __init__(self, root):
        self.root = root
        self.predictor = MedicineEffectivenessPredictor()
        self.theme = setup_theme()
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("Medicine Effectiveness Predictor")
        self.root.geometry("900x600")
        
        # Apply theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.theme["bg_color"])
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Medicine Effectiveness Predictor",
            font=self.theme["font_title"],
            text_color=self.theme["primary_color"]
        )
        self.title_label.pack()
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Predict how effective a medicine will be for a specific condition",
            font=self.theme["font_subtitle"],
            text_color=self.theme["text_secondary"]
        )
        self.subtitle_label.pack()
        
        # Input form
        self.form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.form_frame.pack(fill="x", pady=10)
        
        # Medicine input
        self.medicine_label = ctk.CTkLabel(
            self.form_frame,
            text="Medicine Name:",
            font=self.theme["font_body"]
        )
        self.medicine_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.medicine_entry = ctk.CTkEntry(
            self.form_frame,
            font=self.theme["font_body"],
            width=300,
            placeholder_text="Enter medicine name..."
        )
        self.medicine_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Condition input
        self.condition_label = ctk.CTkLabel(
            self.form_frame,
            text="Medical Condition:",
            font=self.theme["font_body"]
        )
        self.condition_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.condition_combobox = ctk.CTkComboBox(
            self.form_frame,
            font=self.theme["font_body"],
            width=300,
            values=[
                "Fever", "Infection", "Headache", "Cough", "Cold", 
                "Asthma", "Diabetes", "Acidity", "Pain", 
                "Inflammation", "Weakness", "Digestion"
            ],
            state="readonly"
        )
        self.condition_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.condition_combobox.set("Select a condition")
        
        # Predict button
        self.predict_button = ctk.CTkButton(
            self.form_frame,
            text="Predict Effectiveness",
            command=self.predict_effectiveness,
            font=self.theme["font_button"],
            fg_color=self.theme["primary_color"],
            hover_color=self.theme["secondary_color"],
            height=40
        )
        self.predict_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Results display
        self.results_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True)
        
        # Medicine info card
        self.medicine_card = ctk.CTkFrame(
            self.results_frame,
            border_width=2,
            border_color=self.theme["primary_color"],
            corner_radius=10
        )
        self.medicine_card.pack(fill="x", pady=10)
        
        self.medicine_name_label = ctk.CTkLabel(
            self.medicine_card,
            text="Medicine: ",
            font=self.theme["font_subtitle"],
            anchor="w"
        )
        self.medicine_name_label.pack(fill="x", padx=10, pady=(10, 0))
        
        self.medicine_category_label = ctk.CTkLabel(
            self.medicine_card,
            text="Category: ",
            font=self.theme["font_body"],
            anchor="w"
        )
        self.medicine_category_label.pack(fill="x", padx=10)
        
        self.medicine_description_label = ctk.CTkLabel(
            self.medicine_card,
            text="Description: ",
            font=self.theme["font_body"],
            anchor="w",
            wraplength=600
        )
        self.medicine_description_label.pack(fill="x", padx=10, pady=(0, 10))
        
        # Effectiveness display
        self.effectiveness_frame = ctk.CTkFrame(
            self.results_frame,
            border_width=2,
            border_color=self.theme["primary_color"],
            corner_radius=10
        )
        self.effectiveness_frame.pack(fill="x", pady=10)
        
        self.effectiveness_title = ctk.CTkLabel(
            self.effectiveness_frame,
            text="Effectiveness Prediction",
            font=self.theme["font_subtitle"]
        )
        self.effectiveness_title.pack(pady=(10, 5))
        
        self.condition_label = ctk.CTkLabel(
            self.effectiveness_frame,
            text="For condition: ",
            font=self.theme["font_body"]
        )
        self.condition_label.pack()
        
        # Progress bar for effectiveness
        self.effectiveness_progress = ctk.CTkProgressBar(
            self.effectiveness_frame,
            orientation="horizontal",
            height=20,
            width=400,
            progress_color=self.theme["primary_color"]
        )
        self.effectiveness_progress.pack(pady=10)
        self.effectiveness_progress.set(0)
        
        self.effectiveness_value = ctk.CTkLabel(
            self.effectiveness_frame,
            text="0%",
            font=("Roboto Medium", 24),
            text_color=self.theme["primary_color"]
        )
        self.effectiveness_value.pack(pady=(0, 10))
        
        # Relevance indicator
        self.relevance_frame = ctk.CTkFrame(self.effectiveness_frame, fg_color="transparent")
        self.relevance_frame.pack(pady=(0, 10))
        
        self.relevance_label = ctk.CTkLabel(
            self.relevance_frame,
            text="Relevance: ",
            font=self.theme["font_body"]
        )
        self.relevance_label.pack(side="left")
        
        self.relevance_indicator = ctk.CTkLabel(
            self.relevance_frame,
            text="",
            font=self.theme["font_body"],
            text_color=self.theme["error_color"]
        )
        self.relevance_indicator.pack(side="left", padx=5)
        
        # Configure grid weights
        self.form_frame.grid_columnconfigure(1, weight=1)
        
    def predict_effectiveness(self):
        medicine_name = self.medicine_entry.get()
        condition = self.condition_combobox.get()
    
        if not medicine_name:
            messagebox.showerror("Error", "Please enter a medicine name")
            return
        
        if condition == "Select a condition":
            messagebox.showerror("Error", "Please select a medical condition")
            return
        
        try:
            # Get medicine ID first
            medicine_id = Medicine.get_id_by_name(medicine_name)
            if not medicine_id:
                messagebox.showwarning("Not Found", f"Medicine '{medicine_name}' not found")
                self.clear_results_display()
                return
            
            # Get the Medicine object
            medicine_obj = Medicine.get_medicine_by_id(medicine_id)
            if not medicine_obj:
                messagebox.showwarning("Error", "Could not retrieve medicine details")
                self.clear_results_display()
                return
            
            # Get effectiveness prediction
            effectiveness = self.predictor.predict_effectiveness(medicine_name, condition)
        
            # Update display with medicine object attributes
            self.update_results_display(
            effectiveness=effectiveness,
            medicine_name=medicine_obj.get_name(),  # Access name attribute
            category=medicine_obj.get_category(),  # Access category attribute
            description=medicine_obj.get_desc(),  # Access description attribute
            condition=condition
            )
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.clear_results_display()
    
    def update_results_display(self, effectiveness, medicine_name, category, description, condition):
        """Update the display with new results"""
        # Update medicine info
        self.medicine_name_label.configure(text=f"Medicine: {medicine_name}")
        self.medicine_category_label.configure(text=f"Category: {category}")
        self.medicine_description_label.configure(text=f"Description: {description}")
        
        # Update condition
        self.condition_label.configure(text=f"For condition: {condition}")
        
        # Update effectiveness display
        effectiveness_pct = effectiveness * 100
        self.effectiveness_progress.set(effectiveness)
        self.effectiveness_value.configure(text=f"{effectiveness_pct:.1f}%")
        
        # Set color based on effectiveness
        if effectiveness > 0.7:
            color = self.theme["secondary_color"]  # Green
        elif effectiveness > 0.4:
            color = self.theme["warning_color"]    # Orange
        else:
            color = self.theme["error_color"]      # Red
            
        self.effectiveness_progress.configure(progress_color=color)
        self.effectiveness_value.configure(text_color=color)
        
        # Update relevance indicator
        if effectiveness > 0.5:
            self.relevance_indicator.configure(
                text="Highly Relevant",
                text_color=self.theme["secondary_color"]
            )
        elif effectiveness > 0.2:
            self.relevance_indicator.configure(
                text="Moderately Relevant",
                text_color=self.theme["warning_color"]
            )
        else:
            self.relevance_indicator.configure(
                text="Not Relevant",
                text_color=self.theme["error_color"]
            )

if __name__ == "__main__":
    root = ctk.CTk()
    app = MedicinePredictorGUI(root)
    root.mainloop()