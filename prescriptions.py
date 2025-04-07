from database import get_db_connection
from datetime import date
from decimal import Decimal
from medicines import Medicine

class PrescriptionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PrescriptionManager, cls).__new__(cls)
            cls._instance.connection = get_db_connection()
        return cls._instance
    
    def create_prescription(self):
        """Create a new prescription with interactive medicine addition"""
        try:
            cursor = self.connection.cursor()
            
            # Get prescription details
            cursor.execute("SELECT COALESCE(MAX(prescription_id), 0) FROM PRESCRIPTIONS")
            max_id = cursor.fetchone()[0]
            prescription_id = max_id + 1            
            prescription_date = date.today()
            
            # Initialize prescription with 0 total amount
            cursor.execute(
                "INSERT INTO PRESCRIPTIONS (prescription_id, date, total_amount) VALUES (%s, %s, 0.00)",
                (prescription_id, prescription_date)
            )
            
            # Add medicines until user stops
            while True:
                self._add_medicine_to_prescription(cursor, prescription_id)
                if input("Add another medicine? (y/n): ").lower() != 'y':
                    break
            
            self.connection.commit()
            print("Prescription created successfully!")
            
        except Exception as e:
            self.connection.rollback()
            print(f"Error creating prescription: {e}")
        finally:
            cursor.close()
    
    def _add_medicine_to_prescription(self, cursor, prescription_id, medicine_id=None, qty=None):
        """Add a medicine to prescription with quantity and calculate price.
        Can be used interactively or programmatically.
        """
        try:
            # Interactive input if not provided
            if medicine_id is None:
                medicine_name = input("Enter medicine name: ")
                medicine_id = Medicine.get_id_by_name(medicine_name)
            if not medicine_id:
                print("Medicine not found!")
                return
        
            if qty is None:
                qty = int(input("Enter quantity: "))
        
            # Get price of the medicine
            cursor.execute(
            "SELECT price FROM MEDICINES WHERE medicine_id = %s",
            (medicine_id,)
            )
            medicine = cursor.fetchone()
        
            if not medicine:
                print("Medicine not found!")
                return
        
            price = medicine[0]
        
            # Check inventory
            cursor.execute(
            "SELECT SUM(current_quantity) FROM INVENTORY WHERE medicine_id = %s",
            (medicine_id,)
            )
            total_stock = cursor.fetchone()[0] or 0
            print(total_stock)
        
            if total_stock < qty:
                print(f"Not enough stock! Available: {total_stock}")
                return
        
            total_price = Decimal(price) * qty
        
            # Insert into PRESCRIPTION_MEDICINES
            cursor.execute(
            """INSERT INTO PRESCRIPTION_MEDICINES 
            (prescription_id, medicine_id, quantity_bought, total_price)
            VALUES (%s, %s, %s, %s)""",
            (prescription_id, medicine_id, qty, total_price)
            )
            print('added the medicine')
        
            # Update prescription total
            cursor.execute(
            "UPDATE PRESCRIPTIONS SET total_amount = total_amount + %s WHERE prescription_id = %s",
            (total_price, prescription_id)
            )
        
            # FIFO inventory deduction
            cursor.execute(
            """SELECT inventory_id, current_quantity 
            FROM INVENTORY 
            WHERE medicine_id = %s AND current_quantity > 0
            ORDER BY expiry_date, date_added""",
            (medicine_id,)
            )
            batches = cursor.fetchall()
        
            remaining = qty
            for batch_id, batch_qty in batches:
                deduct = min(remaining, batch_qty)
                cursor.execute(
                "UPDATE INVENTORY SET current_quantity = current_quantity - %s WHERE inventory_id = %s",
                (deduct, batch_id)
                )
                remaining -= deduct
                if remaining == 0:
                    break
    
        except Exception as e:
            print(f"Error adding medicine: {e}")
            raise
    
    def read_prescription(self, prescription_id):
        """Read prescription details"""
        try:
            cursor = self.connection.cursor(dictionary=True)
        
            # Get prescription header
            cursor.execute(
            "SELECT * FROM PRESCRIPTIONS WHERE prescription_id = %s",
            (prescription_id,)
            )
            prescription = cursor.fetchone()
        
            if not prescription:
                print("Prescription not found!")
                return None  # Explicitly return None
        
            # Get prescription medicines
            cursor.execute(
            """SELECT m.name, m.manufacturer, m.price, pm.quantity_bought, pm.total_price
            FROM PRESCRIPTION_MEDICINES pm
            JOIN MEDICINES m ON pm.medicine_id = m.medicine_id
            WHERE pm.prescription_id = %s""",
            (prescription_id,)
            )
            medicines = cursor.fetchall()
        
            # Print prescription details
            print("\nPrescription Details:")
            print(f"ID: {prescription['prescription_id']}")
            print(f"Date: {prescription['date']}")
            print(f"Total Amount: {prescription['total_amount']:.2f}")
        
            print("\nMedicines:")
            for med in medicines:
                print(f"{med['name']} ({med['manufacturer']}) - "
                f"Qty: {med['quantity_bought']} - "
                f"Price: {med['total_price']:.2f}")
        
            prescription['medicines'] = medicines
        
            return prescription

        except Exception as e:
            print(f"Error reading prescription: {e}")
            return None
        finally:
            cursor.close()

    
    def update_prescription(self, prescription_id):
        """Update prescription by adding/removing medicines"""
        try:
            cursor = self.connection.cursor()
            
            # Verify prescription exists
            cursor.execute(
                "SELECT 1 FROM PRESCRIPTIONS WHERE prescription_id = %s",
                (prescription_id,)
            )
            if not cursor.fetchone():
                print("Prescription not found!")
                return
            
            while True:
                print("\n1. Add medicine")
                print("2. Remove medicine")
                print("3. Finish updating")
                choice = input("Select option: ")
                
                if choice == '1':
                    self._add_medicine_to_prescription(cursor, prescription_id)
                elif choice == '2':
                    self._remove_medicine_from_prescription(cursor, prescription_id)
                elif choice == '3':
                    break
                else:
                    print("Invalid choice!")
            
            self.connection.commit()
            print("Prescription updated successfully!")
            
        except Exception as e:
            self.connection.rollback()
            print(f"Error updating prescription: {e}")
        finally:
            cursor.close()
    
    def _remove_medicine_from_prescription(self, cursor, prescription_id):
        """Remove a medicine from prescription and adjust totals"""
        try:
            medicine_name = input("Enter medicine name to remove: ")
            medicine_id = Medicine.get_id_by_name(medicine_name)
            if not medicine_id:
                print("Medicine not found!")
                return
            
            # Get medicine details from prescription
            cursor.execute(
                """SELECT quantity_bought, total_price 
                FROM PRESCRIPTION_MEDICINES 
                WHERE prescription_id = %s AND medicine_id = %s""",
                (prescription_id, medicine_id)
            )
            medicine = cursor.fetchone()
            
            if not medicine:
                print("Medicine not found in this prescription!")
                return
            
            quantity, total_price = medicine
            
            # Remove from prescription_medicines
            cursor.execute(
                """DELETE FROM PRESCRIPTION_MEDICINES 
                WHERE prescription_id = %s AND medicine_id = %s""",
                (prescription_id, medicine_id)
            )
            
            # Update prescription total amount
            cursor.execute(
                "UPDATE PRESCRIPTIONS SET total_amount = total_amount - %s WHERE prescription_id = %s",
                (total_price, prescription_id)
            )
            
            # Restore medicine to inventory - add to newest batch
            cursor.execute(
                """SELECT inventory_id 
                FROM INVENTORY 
                WHERE medicine_id = %s
                ORDER BY date_added DESC
                LIMIT 1""",
                (medicine_id,)
            )
            batch = cursor.fetchone()
            
            if batch:
                cursor.execute(
                    "UPDATE INVENTORY SET current_quantity = current_quantity + %s WHERE inventory_id = %s",
                    (quantity, batch[0])
                )
            else:
                # If no batch exists, create a new one
                cursor.execute(
                    """INSERT INTO INVENTORY 
                    (medicine_id, supplier_id, quantity_added, current_quantity, batch_number, expiry_date)
                    VALUES (%s, 1, %s, %s, 'RETURN-'+%s, DATE_ADD(CURDATE(), INTERVAL 1 YEAR))""",
                    (medicine_id, quantity, quantity, prescription_id)
                )
                
        except Exception as e:
            print(f"Error removing medicine: {e}")
            raise
    
    def delete_prescription(self, prescription_id):
        """Delete a prescription and restore medicine stocks"""
        try:
            cursor = self.connection.cursor()
            
            # First restore all medicine stocks
            cursor.execute(
                """SELECT medicine_id, quantity_bought 
                FROM PRESCRIPTION_MEDICINES 
                WHERE prescription_id = %s""",
                (prescription_id,)
            )
            medicines = cursor.fetchall()
            
            for med_id, qty in medicines:
                # Restore to newest batch
                cursor.execute(
                    """SELECT inventory_id 
                    FROM INVENTORY 
                    WHERE medicine_id = %s
                    ORDER BY date_added DESC
                    LIMIT 1""",
                    (med_id,)
                )
                batch = cursor.fetchone()
                
                if batch:
                    cursor.execute(
                        "UPDATE INVENTORY SET current_quantity = current_quantity + %s WHERE inventory_id = %s",
                        (qty, batch[0])
                    )
                else:
                    # If no batch exists, create a new one
                    cursor.execute(
                        """INSERT INTO INVENTORY 
                        (medicine_id, supplier_id, quantity_added, current_quantity, batch_number, expiry_date)
                        VALUES (%s, 1, %s, %s, 'RETURN-'+%s, DATE_ADD(CURDATE(), INTERVAL 1 YEAR))""",
                        (med_id, qty, qty, prescription_id)
                    )
            
            # Delete prescription medicines
            cursor.execute(
                "DELETE FROM PRESCRIPTION_MEDICINES WHERE prescription_id = %s",
                (prescription_id,)
            )
            
            # Delete prescription
            cursor.execute(
                "DELETE FROM PRESCRIPTIONS WHERE prescription_id = %s",
                (prescription_id,)
            )
            
            self.connection.commit()
            print("Prescription deleted successfully!")
            
        except Exception as e:
            self.connection.rollback()
            print(f"Error deleting prescription: {e}")
        finally:
            cursor.close()

    def get_prescriptions_by_date(self, target_date):
        """Get all prescriptions for a specific date"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM PRESCRIPTIONS WHERE date = %s ORDER BY prescription_id",
                (target_date,)
            )
            prescriptions = cursor.fetchall()
            
            if not prescriptions:
                print(f"No prescriptions found for {target_date}")
                return
                
            print(f"\nPrescriptions for {target_date}:")
            for pres in prescriptions:
                print(f"ID: {pres['prescription_id']} - Total: ${pres['total_amount']:.2f}")
            return prescriptions
        except Exception as e:
            print(f"Error retrieving prescriptions: {e}")
        finally:
            cursor.close()

    def get_prescriptions_by_amount_range(self, min_amount, max_amount):
        """Get prescriptions within a specific amount range"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM PRESCRIPTIONS WHERE total_amount BETWEEN %s AND %s ORDER BY total_amount",
                (min_amount, max_amount)
            )
            prescriptions = cursor.fetchall()
            
            if not prescriptions:
                print(f"No prescriptions found between ${min_amount:.2f} and ${max_amount:.2f}")
                return
                
            print(f"\nPrescriptions between ${min_amount:.2f}-${max_amount:.2f}:")
            for pres in prescriptions:
                print(f"ID: {pres['prescription_id']} - Date: {pres['date']} - Total: ${pres['total_amount']:.2f}")
            return prescriptions
        except Exception as e:
            print(f"Error retrieving prescriptions: {e}")
        finally:
            cursor.close()

    def update_prescription_medicine(self, prescription_id, medicine_id,quantity=None):
        """Update specific medicine in a prescription"""
        try:
            cursor = self.connection.cursor()
            
            # Get current quantity
            cursor.execute(
                "SELECT quantity_bought FROM PRESCRIPTION_MEDICINES WHERE prescription_id = %s AND medicine_id = %s",
                (prescription_id, medicine_id)
            )
            current_qty = cursor.fetchone()
            
            if not current_qty:
                print("This medicine is not in the specified prescription")
                return
            if quantity is None:
                new_qty = int(input(f"Current quantity: {current_qty[0]}. Enter new quantity: "))
            else:
                new_qty=quantity
            
            # Calculate difference
            qty_diff = new_qty - current_qty[0]
            
            if qty_diff == 0:
                print("No changes made")
                return
                
            # Get medicine price
            cursor.execute(
                "SELECT price FROM MEDICINES WHERE medicine_id = %s",
                (medicine_id,)
            )
            price = cursor.fetchone()[0]
            
            # Update prescription_medicines
            cursor.execute(
                """UPDATE PRESCRIPTION_MEDICINES 
                SET quantity_bought = %s, total_price = %s 
                WHERE prescription_id = %s AND medicine_id = %s""",
                (new_qty, price * new_qty, prescription_id, medicine_id)
            )
            
            # Update prescription total
            amount_diff = Decimal(price) * qty_diff
            cursor.execute(
                "UPDATE PRESCRIPTIONS SET total_amount = total_amount + %s WHERE prescription_id = %s",
                (amount_diff, prescription_id)
            )
            
            # Update inventory
            if qty_diff > 0:
                # Deduct from oldest batch
                cursor.execute(
                    """SELECT inventory_id, current_quantity 
                    FROM INVENTORY 
                    WHERE medicine_id = %s AND current_quantity > 0
                    ORDER BY expiry_date, date_added""",
                    (medicine_id,)
                )
                batches = cursor.fetchall()
                
                remaining = qty_diff
                for batch in batches:
                    batch_id, batch_qty = batch
                    deduct = min(remaining, batch_qty)
                    
                    cursor.execute(
                        "UPDATE INVENTORY SET current_quantity = current_quantity - %s WHERE inventory_id = %s",
                        (deduct, batch_id)
                    )
                    
                    remaining -= deduct
                    if remaining == 0:
                        break
            else:
                # Add to newest batch
                cursor.execute(
                    """SELECT inventory_id 
                    FROM INVENTORY 
                    WHERE medicine_id = %s
                    ORDER BY date_added DESC
                    LIMIT 1""",
                    (medicine_id,)
                )
                batch = cursor.fetchone()
                
                if batch:
                    cursor.execute(
                        "UPDATE INVENTORY SET current_quantity = current_quantity + %s WHERE inventory_id = %s",
                        (-qty_diff, batch[0])
                    )
                else:
                    # If no batch exists, create a new one
                    cursor.execute(
                        """INSERT INTO INVENTORY 
                        (medicine_id, supplier_id, quantity_added, current_quantity, batch_number, expiry_date)
                        VALUES (%s, 1, %s, %s, 'ADJUST-'+%s, DATE_ADD(CURDATE(), INTERVAL 1 YEAR))""",
                        (medicine_id, -qty_diff, -qty_diff, prescription_id)
                    )
            
            self.connection.commit()
            print("Prescription medicine updated successfully!")
            
        except Exception as e:
            self.connection.rollback()
            print(f"Error updating prescription medicine: {e}")
        finally:
            cursor.close()

    def remove_medicine_from_prescription(self, prescription_id, medicine_id):
        """Remove specific medicine from prescription"""
        try:
            cursor = self.connection.cursor()
            
            # Get medicine details from prescription
            cursor.execute(
                """SELECT quantity_bought, total_price 
                FROM PRESCRIPTION_MEDICINES 
                WHERE prescription_id = %s AND medicine_id = %s""",
                (prescription_id, medicine_id)
            )
            medicine = cursor.fetchone()
            
            if not medicine:
                print("Medicine not found in this prescription!")
                return
                
            quantity, total_price = medicine
            
            # Remove from prescription_medicines
            cursor.execute(
                """DELETE FROM PRESCRIPTION_MEDICINES 
                WHERE prescription_id = %s AND medicine_id = %s""",
                (prescription_id, medicine_id)
            )
            
            # Update prescription total
            cursor.execute(
                "UPDATE PRESCRIPTIONS SET total_amount = total_amount - %s WHERE prescription_id = %s",
                (total_price, prescription_id)
            )
            
            # Restore inventory
            cursor.execute(
                """SELECT inventory_id 
                FROM INVENTORY 
                WHERE medicine_id = %s
                ORDER BY date_added DESC
                LIMIT 1""",
                (medicine_id,)
            )
            batch = cursor.fetchone()
            
            if batch:
                cursor.execute(
                    "UPDATE INVENTORY SET current_quantity = current_quantity + %s WHERE inventory_id = %s",
                    (quantity, batch[0])
                )
            else:
                # If no batch exists, create a new one
                cursor.execute(
                    """INSERT INTO INVENTORY 
                    (medicine_id, supplier_id, quantity_added, current_quantity, batch_number, expiry_date)
                    VALUES (%s, 1, %s, %s, 'RETURN-'+%s, DATE_ADD(CURDATE(), INTERVAL 1 YEAR))""",
                    (medicine_id, quantity, quantity, prescription_id)
                )
            
            self.connection.commit()
            print("Medicine removed from prescription successfully!")
            
        except Exception as e:
            self.connection.rollback()
            print(f"Error removing medicine from prescription: {e}")
        finally:
            cursor.close()

    def adjust_inventory_quantity(self, medicine_id, adjustment):
        """Adjust medicine quantity in inventory"""
        try:
            cursor = self.connection.cursor()
            
            # Check current stock
            cursor.execute(
                "SELECT SUM(current_quantity) FROM INVENTORY WHERE medicine_id = %s",
                (medicine_id,)
            )
            current_stock = cursor.fetchone()[0] or 0
            
            new_stock = current_stock + adjustment
            if new_stock < 0:
                print(f"Cannot adjust below 0. Current stock: {current_stock}")
                return
                
            # Update inventory
            if adjustment > 0:
                # Add to newest batch
                cursor.execute(
                    """SELECT inventory_id 
                    FROM INVENTORY 
                    WHERE medicine_id = %s
                    ORDER BY date_added DESC
                    LIMIT 1""",
                    (medicine_id,)
                )
                batch = cursor.fetchone()
                
                if batch:
                    cursor.execute(
                        "UPDATE INVENTORY SET current_quantity = current_quantity + %s WHERE inventory_id = %s",
                        (adjustment, batch[0])
                    )
                else:
                    # If no batch exists, create a new one
                    cursor.execute(
                        """INSERT INTO INVENTORY 
                        (medicine_id, supplier_id, quantity_added, current_quantity, batch_number, expiry_date)
                        VALUES (%s, 1, %s, %s, 'ADJUST-'+%s, DATE_ADD(CURDATE(), INTERVAL 1 YEAR))""",
                        (medicine_id, adjustment, adjustment, 'ADJUST')
                    )
            else:
                # Deduct from oldest batches first
                remaining = -adjustment
                cursor.execute(
                    """SELECT inventory_id, current_quantity 
                    FROM INVENTORY 
                    WHERE medicine_id = %s AND current_quantity > 0
                    ORDER BY expiry_date, date_added""",
                    (medicine_id,)
                )
                batches = cursor.fetchall()
                
                for batch in batches:
                    batch_id, batch_qty = batch
                    deduct = min(remaining, batch_qty)
                    
                    cursor.execute(
                        "UPDATE INVENTORY SET current_quantity = current_quantity - %s WHERE inventory_id = %s",
                        (deduct, batch_id)
                    )
                    
                    remaining -= deduct
                    if remaining == 0:
                        break
            
            self.connection.commit()
            print(f"Inventory updated. New stock: {new_stock}")
            
        except Exception as e:
            self.connection.rollback()
            print(f"Error adjusting inventory: {e}")
        finally:
            cursor.close()

    def check_medicine_availability(self, medicine_id):
        """Check if medicine exists and is in stock"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT SUM(current_quantity) FROM INVENTORY WHERE medicine_id = %s",
                (medicine_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                print("Medicine not found in database")
                return False
                
            stock = result[0] or 0
            return stock 
            
        except Exception as e:
            print(f"Error checking medicine availability: {e}")
            return False
        finally:
            cursor.close()