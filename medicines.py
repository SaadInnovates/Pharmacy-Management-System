from database import get_db_connection
from datetime import date

class Medicine:
    def __init__(self, name, manufacturer, price, category, description=None, dosage=None, requires_prescription=False):
        self.__name = name
        self.__manufacturer = manufacturer
        self.__price = price
        self.__category = category
        self.__description = description
        self.__dosage = dosage
        self.__requires_prescription = requires_prescription

    def get_name(self):
        return self.__name
    
    def get_desc(self):
        return self.__description
    
    def get_category(self):
        return self.__category
    
    def add_in_db(self):
        """Stores medicine in the database with an auto-assigned ID, preventing duplicates."""

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Check if the medicine already exists
            cursor.execute("SELECT * FROM medicines WHERE name = %s", (self.__name,))
            if cursor.fetchone():
                print(f"Error: Medicine '{self.__name}' already exists in the database!")
                return
        
            # Get the next medicine_id
            cursor.execute("SELECT MAX(medicine_id) AS max_id FROM medicines")
            result = cursor.fetchone()
            next_id = 1 if result["max_id"] is None else result["max_id"] + 1

            # Insert new medicine record
            query = """INSERT INTO medicines 
                      (medicine_id, name, manufacturer, price, category, description, dosage, requires_prescription) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (
                next_id, 
                self.__name, 
                self.__manufacturer, 
                self.__price, 
                self.__category,
                self.__description,
                self.__dosage,
                self.__requires_prescription
            )
            cursor.execute(query, values)
            conn.commit()
            print("Medicine stored in the database successfully!")

        except Exception as e:
            print("Error adding medicine:", e)

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def read_all_medicines():
        """Retrieves and displays all medicines from the database with their current stock."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get medicines with their total current stock
            query = """
                SELECT m.*, COALESCE(SUM(i.current_quantity), 0) AS total_stock
                FROM medicines m
                LEFT JOIN inventory i ON m.medicine_id = i.medicine_id
                GROUP BY m.medicine_id
            """
            cursor.execute(query)
            medicines = cursor.fetchall()

            if not medicines:
                print("No medicines found in the database.")
                return

            print("\n[ Medicines List ]")
            print("------------------------------------------------------------------------------------------------------------------")
            print(f"{'ID':<5} {'Name':<20} {'Manufacturer':<15} {'Price':<10} {'Stock':<10} {'Category':<15} {'Prescription'}")
            print("------------------------------------------------------------------------------------------------------------------")
            for medicine in medicines:
                prescription = "Yes" if medicine['requires_prescription'] else "No"
                print(f"{medicine['medicine_id']:<5} {medicine['name']:<20} {medicine['manufacturer']:<15} "
                      f"{medicine['price']:<10.2f} {medicine['total_stock']:<10} {medicine['category']:<15} {prescription}")
            print("------------------------------------------------------------------------------------------------------------------")
            return medicines
        except Exception as e:
            print("Error reading medicines:", e)

        finally:
            cursor.close()
            conn.close()

    def update_medicine(self, new_price=None, new_category=None, new_description=None, new_dosage=None, new_prescription=None):
        """Updates medicine details in the database."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get current values if new ones aren't provided
            current = Medicine.get_medicine_by_name(self.__name)
            if not current:
                print(f"Medicine '{self.__name}' not found in database!")
                return

            query = """
                UPDATE medicines 
                SET price=%s, category=%s, description=%s, dosage=%s, requires_prescription=%s
                WHERE name=%s
            """
            values = (
                new_price if new_price is not None else current['price'],
                new_category if new_category is not None else current['category'],
                new_description if new_description is not None else current['description'],
                new_dosage if new_dosage is not None else current['dosage'],
                new_prescription if new_prescription is not None else current['requires_prescription'],
                self.__name
            )
            cursor.execute(query, values)
            conn.commit()
            print("Medicine details updated successfully!")

        except Exception as e:
            print("Error updating medicine:", e)

        finally:
            cursor.close()
            conn.close()

    def delete_medicine(self):
        """Deletes the medicine from the database after checking inventory."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # First check if medicine exists in inventory
            cursor.execute("SELECT SUM(current_quantity) AS total FROM inventory WHERE medicine_id = "
                         "(SELECT medicine_id FROM medicines WHERE name = %s)", (self.__name,))
            result = cursor.fetchone()
            
            if result['total'] and result['total'] > 0:
                print(f"Cannot delete medicine '{self.__name}' - it still has inventory stock!")
                return

            cursor.execute("DELETE FROM medicines WHERE name=%s", (self.__name,))
            conn.commit()
            print("Medicine deleted successfully!")

        except Exception as e:
            print("Error deleting medicine:", e)

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_expired_medicines():
        """Fetches and displays expired medicines from inventory."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT m.medicine_id, m.name, m.manufacturer, m.price, 
                       i.batch_number, i.current_quantity, i.expiry_date
                FROM medicines m
                JOIN inventory i ON m.medicine_id = i.medicine_id
                WHERE i.expiry_date < %s AND i.current_quantity > 0
                ORDER BY i.expiry_date
            """
            cursor.execute(query, (date.today(),))
            expired_medicines = cursor.fetchall()

            if not expired_medicines:
               print("No expired medicines found in inventory.")
               return

            print("\n[ Expired Medicines in Inventory ]")
            print("--------------------------------------------------------------------------------------------------")
            print(f"{'ID':<5} {'Name':<20} {'Batch':<15} {'Qty':<5} {'Expiry Date':<12} {'Price':<10}")
            print("--------------------------------------------------------------------------------------------------")
            for med in expired_medicines:
                formatted_date = med['expiry_date'].strftime('%d-%m-%Y')
                print(f"{med['medicine_id']:<5} {med['name']:<20} {med['batch_number']:<15} "
                      f"{med['current_quantity']:<5} {formatted_date:<12} {med['price']:<10.2f}")
            print("--------------------------------------------------------------------------------------------------")
            return expired_medicines
        except Exception as e:
            print("Error fetching expired medicines:", e)

        finally:
            cursor.close()
            conn.close()

    def display(self):
        """Displays medicine details."""
        print('Medicine:', self.__name)
        print('Manufacturer:', self.__manufacturer)
        print('Price:', self.__price)
        print('Category:', self.__category)
        print('Description:', self.__description)
        print('Dosage:', self.__dosage)
        print('Requires Prescription:', "Yes" if self.__requires_prescription else "No")

    @staticmethod
    def get_medicine_by_name(name):
        """Fetches a medicine from the database by name."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM medicines WHERE name = %s", (name,))
            medicine = cursor.fetchone()
            if not medicine:
               print(f"Medicine '{name}' not found in the database.")
            return medicine
        except Exception as e:
            print("Error fetching medicine:", e)
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_id_by_name(name):
        """Fetches the medicine_id from the database by name."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT medicine_id FROM medicines WHERE name = %s", (name,))
            medicine = cursor.fetchone()
            if not medicine:
                print(f"Medicine '{name}' not found in the database.")
                return None
            return medicine['medicine_id']
        except Exception as e:
            print("Error fetching medicine ID:", e)
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_low_stock_medicines(threshold=10):
        """Returns medicines with total stock below threshold"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT m.medicine_id, m.name, m.manufacturer, 
                       SUM(i.current_quantity) AS total_stock
                FROM medicines m
                JOIN inventory i ON m.medicine_id = i.medicine_id
                GROUP BY m.medicine_id
                HAVING total_stock < %s
                ORDER BY total_stock ASC
            """
            cursor.execute(query, (threshold,))
            low_stock = cursor.fetchall()
            
            if not low_stock:
                print(f"No medicines below {threshold} units.")
                return
                
            print("\n[ Low Stock Alert ]")
            print("-"*60)
            print(f"{'ID':<5}{'Name':<20}{'Manufacturer':<20}{'Stock':<10}")
            print("-"*60)
            for item in low_stock:
                print(f"{item['medicine_id']:<5}{item['name']:<20}{item['manufacturer']:<20}{item['total_stock']:<10}")
            print("-"*60)
            return low_stock
            
        except Exception as e:
            print("Error checking low stock:", e)
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_nearly_expiring_medicines(days=30):
        """Returns batches expiring within specified days"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT m.name, i.batch_number, i.expiry_date, 
                       i.current_quantity, DATEDIFF(i.expiry_date, CURDATE()) AS days_left
                FROM inventory i
                JOIN medicines m ON i.medicine_id = m.medicine_id
                WHERE i.expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
                AND i.current_quantity > 0
                ORDER BY i.expiry_date ASC
            """
            cursor.execute(query, (days,))
            expiring = cursor.fetchall()
            
            if not expiring:
                print(f"No medicines expiring within {days} days.")
                return
                
            print(f"\n[ Expiring Within {days} Days ]")
            print("-"*80)
            print(f"{'Medicine':<20}{'Batch':<15}{'Expiry Date':<12}{'Qty':<6}{'Days Left':<10}")
            print("-"*80)
            for item in expiring:
                exp_date = item['expiry_date'].strftime('%d-%m-%Y')
                print(f"{item['name']:<20}{item['batch_number']:<15}{exp_date:<12}{item['current_quantity']:<6}{item['days_left']:<10}")
            print("-"*80)
            return expiring
            
        except Exception as e:
            print("Error checking expiry:", e)
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def search_medicines(search_term):
        """Searches by name, manufacturer, or category"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT m.*, COALESCE(SUM(i.current_quantity), 0) AS stock
                FROM medicines m
                LEFT JOIN inventory i ON m.medicine_id = i.medicine_id
                WHERE m.name LIKE %s OR m.manufacturer LIKE %s OR m.category LIKE %s
                GROUP BY m.medicine_id
            """
            param = f"%{search_term}%"
            cursor.execute(query, (param, param, param))
            results = cursor.fetchall()
            
            if not results:
                print("No matching medicines found.")
                return
                
            print("\n[ Search Results ]")
            print("-"*90)
            print(f"{'ID':<5}{'Name':<20}{'Manufacturer':<20}{'Price':<10}{'Stock':<10}{'Category':<15}")
            print("-"*90)
            for med in results:
                print(f"{med['medicine_id']:<5}{med['name']:<20}{med['manufacturer']:<20}"
                      f"{med['price']:<10.2f}{med['stock']:<10}{med['category']:<15}")
            print("-"*90)
            return results
            
        except Exception as e:
            print("Search error:", e)
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_medicine_by_id(medicine_id):
        """Get medicine details by ID from the database"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
        
            query = """
            SELECT 
            medicine_id,
            name,
            manufacturer,
            price,
            category,
            description,
            dosage,
            requires_prescription
            FROM medicines 
            WHERE medicine_id = %s
            """
            cursor.execute(query, (medicine_id,))
            medicine = cursor.fetchone()
        
            return Medicine(
            name=medicine['name'],
            manufacturer=medicine['manufacturer'],
            price=float(medicine['price']),
            category=medicine['category'],
            description=medicine['description'],
            dosage=medicine['dosage'],
            requires_prescription=bool(medicine['requires_prescription'])
        )
        
        except Exception as e:
            print(f"Error fetching medicine by ID: {str(e)}")
            return None
        finally:
            if cursor:
               cursor.close()
            if conn and conn.is_connected():
               conn.close()