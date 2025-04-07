from database import get_db_connection

class MedicineEffectivenessPredictor:
    def __init__(self):
        # Initialize the connection here
        self.conn = get_db_connection()
        # Create the cursor after getting the connection
        self.cur = self.conn.cursor()

    def predict_effectiveness(self, medicine_name, condition):
        """
        Predicts the effectiveness of a medicine for a given condition based on
        condition mappings and medicine category adjustments.
        """
        # Step 1: Fetch medicine details
        self.cur.execute("SELECT medicine_id, name, category, description FROM medicines WHERE name = %s", (medicine_name,))
        med = self.cur.fetchone()
    
        if not med:
           print("\n[!] Medicine not found.")
           return 0.0

        medicine_id, medicine_name, category, description = med
        print(f"\n[INFO] Medicine: {medicine_name}, Category: {category}")

        # Step 2: Base effectiveness
        base_effectiveness = 0.85

        # Step 3: Condition mappings
        condition_effectiveness_map = {
        "fever": 0.90,
        "infection": 0.80,
        "headache": 0.85,
        "cough": 0.75,
        "cold": 0.70,
        "asthma": 0.65,
        "diabetes": 0.88,
        "acidity": 0.78,
        "pain": 0.83,
        "inflammation": 0.79,
        "weakness": 0.72,
        "digestion": 0.76
        }
        condition_prob = condition_effectiveness_map.get(condition.lower(), 0.70)
        print(f"[INFO] Condition '{condition}' → base probability: {condition_prob}")

        # Step 4: Relevance mapping (condition → valid categories)
        condition_category_map = {
        "diabetes": ["diabetes"],
        "headache": ["painkiller"],
        "fever": ["painkiller", "antibiotic"],
        "infection": ["antibiotic"],
        "cough": ["respiratory", "antibiotic"],
        "cold": ["respiratory"],
        "asthma": ["respiratory"],
        "acidity": ["digestive", "antacid"],
        "pain": ["painkiller"],
        "digestion": ["digestive"],
        "weakness": ["vitamin supplement"],
        "inflammation": ["painkiller", "antibiotic"]
        }

        # Step 5: Category effectiveness map
        category_effectiveness_map = {
        "painkiller": 0.05,
        "antibiotic": 0.10,
        "respiratory": 0.07,
        "digestive": 0.04,
        "vitamin supplement": 0.06,
        "diabetes": 0.06,
        "antiviral": 0.08,
        "antifungal": 0.06,
        "antacid": 0.03,
        "immunity booster": 0.05,
        "combination": 0.03
        }

        # Normalize
        category_key = category.lower()
        is_relevant = category_key in condition_category_map.get(condition.lower(), [])

        # If relevant, apply full adjustment, otherwise reduce effectiveness drastically
        if is_relevant:
            adjustment = category_effectiveness_map.get(category_key, 0.02)
            base_effectiveness += adjustment
            print(f"[INFO] Relevant category! Adjustment: +{adjustment}")
            return base_effectiveness
        else:
            print(f"[INFO] Irrelevant category for condition '{condition}'. Reducing effectiveness.")
            return 0.1  # Effectiveness very low due to mismatch