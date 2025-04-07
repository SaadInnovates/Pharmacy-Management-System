from datetime import datetime, timedelta
from database import get_db_connection
from medicines import Medicine
import mysql.connector

class PharmacyInventory:
    def __init__(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def _get_next_inventory_id(self):
        """Manually get the next available inventory ID"""
        self.cursor.execute("SELECT MAX(inventory_id) FROM inventory")
        result = self.cursor.fetchone()
        return (result['MAX(inventory_id)'] or 0) + 1

    def add_inventory_item(self, medicine_id, supplier_id, quantity_added, batch_number, expiry_date, location):
        """Add new inventory item with manual ID generation matching the table structure"""
        try:
            # Validate quantity
            if quantity_added <= 0:
                return {"success": False, "message": "Quantity must be positive"}

            # Check medicine exists
            self.cursor.execute("SELECT 1 FROM medicines WHERE medicine_id = %s", (medicine_id,))
            if not self.cursor.fetchone():
                return {"success": False, "message": f"Medicine ID {medicine_id} not found"}

            # Validate supplier exists
            self.cursor.execute("SELECT 1 FROM suppliers WHERE supplier_id = %s", (supplier_id,))
            if not self.cursor.fetchone():
                return {"success": False, "message": f"Supplier ID {supplier_id} not found"}

            # Validate expiry date
            try:
                expiry = datetime.strptime(expiry_date, '%Y-%m-%d').date()
                if expiry <= datetime.now().date():
                    return {"success": False, "message": "Expiry date must be in the future"}
            except ValueError:
                return {"success": False, "message": "Invalid date format. Use YYYY-MM-DD"}

            # Manually generate the next ID
            inventory_id = self._get_next_inventory_id()

            # Insert new record matching your table structure exactly
            query = """
            INSERT INTO inventory (
                inventory_id,
                medicine_id,
                supplier_id,
                quantity_added,
                date_added,
                batch_number,
                expiry_date,
                current_quantity,
                location
            ) VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s, %s)
            """
            params = (
                inventory_id,
                medicine_id,
                supplier_id,
                quantity_added,
                batch_number,
                expiry_date,
                quantity_added,  # current_quantity starts same as quantity_added
                location
            )

            self.cursor.execute(query, params)
            self.conn.commit()

            return {
                "success": True,
                "message": "Inventory item added successfully",
                "inventory_id": inventory_id,
                "details": {
                    "medicine_id": medicine_id,
                    "quantity_added": quantity_added,
                    "batch_number": batch_number,
                    "expiry_date": expiry_date,
                    "location": location
                }
            }

        except mysql.connector.Error as db_error:
            self.conn.rollback()
            error_msg = f"Database error ({db_error.errno}): {db_error.msg}"
            if db_error.errno == 1062:  # Duplicate entry
                error_msg = "Inventory ID or batch number already exists"
            return {"success": False, "message": error_msg}
        except Exception as e:
            self.conn.rollback()
            return {"success": False, "message": f"Unexpected error: {str(e)}"}

    def update_inventory_quantity(self, inventory_id, new_quantity):
        """Update current quantity of an inventory item"""
        try:
            query = "UPDATE inventory SET current_quantity = %s WHERE inventory_id = %s"
            self.cursor.execute(query, (new_quantity, inventory_id))
            self.conn.commit()
            return {"success": True, "message": "Quantity updated successfully"}
        except Exception as e:
            self.conn.rollback()
            return {"success": False, "message": f"Error updating quantity: {str(e)}"}

    def get_low_stock_items(self, threshold=10):
        """Get items with current quantity below threshold"""
        try:
            query = """
            SELECT i.*, m.name as medicine_name 
            FROM inventory i
            JOIN medicines m ON i.medicine_id = m.medicine_id
            WHERE i.current_quantity < %s
            """
            self.cursor.execute(query, (threshold,))
            return self.cursor.fetchall()
        except Exception as e:
            return {"error": f"Error fetching low stock items: {str(e)}"}

    def get_expiring_soon(self, days=30):
        """Get items expiring within specified days"""
        try:
            expiry_date = datetime.now().date() + timedelta(days=days)
            query = """
            SELECT i.*, m.name as medicine_name, DATEDIFF(i.expiry_date, CURDATE()) as days_until_expiry
            FROM inventory i
            JOIN medicines m ON i.medicine_id = m.medicine_id
            WHERE i.expiry_date BETWEEN CURDATE() AND %s
            ORDER BY i.expiry_date ASC
            """
            self.cursor.execute(query, (expiry_date,))
            return self.cursor.fetchall()
        except Exception as e:
            return {"error": f"Error fetching expiring items: {str(e)}"}

    def transfer_inventory(self, inventory_id, new_location, quantity):
        """Transfer inventory between locations with quantity adjustment"""
        try:
            # Check available quantity
            self.cursor.execute("""
                SELECT current_quantity, medicine_id, supplier_id, batch_number, expiry_date 
                FROM inventory 
                WHERE inventory_id = %s
            """, (inventory_id,))
            source_item = self.cursor.fetchone()
            
            if not source_item:
                return {"success": False, "message": "Source inventory item not found"}
                
            if quantity > source_item['current_quantity']:
                return {"success": False, "message": "Not enough quantity available"}

            # Generate new inventory ID
            new_inventory_id = self._get_next_inventory_id()

            # Create new inventory record at new location
            insert_query = """
            INSERT INTO inventory (
                inventory_id,
                medicine_id,
                supplier_id,
                quantity_added,
                date_added,
                batch_number,
                expiry_date,
                current_quantity,
                location
            ) VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s, %s)
            """
            self.cursor.execute(insert_query, (
                new_inventory_id,
                source_item['medicine_id'],
                source_item['supplier_id'],
                quantity,
                source_item['batch_number'],
                source_item['expiry_date'],
                quantity,
                new_location
            ))
            
            # Update original inventory
            update_query = """
            UPDATE inventory 
            SET current_quantity = current_quantity - %s 
            WHERE inventory_id = %s
            """
            self.cursor.execute(update_query, (quantity, inventory_id))
            
            self.conn.commit()
            
            return {
                "success": True, 
                "message": "Inventory transferred successfully",
                "new_inventory_id": new_inventory_id,
                "remaining_quantity": source_item['current_quantity'] - quantity
            }
            
        except Exception as e:
            self.conn.rollback()
            return {"success": False, "message": f"Error transferring inventory: {str(e)}"}

    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

            # Reporting Functions
    def generate_inventory_report(self):
        """Generate comprehensive inventory report"""
        try:
            query = """
            SELECT 
                m.name as medicine_name,
                SUM(i.current_quantity) as total_quantity,
                COUNT(DISTINCT i.batch_number) as batch_count,
                MIN(i.expiry_date) as earliest_expiry,
                GROUP_CONCAT(DISTINCT i.location) as locations
            FROM INVENTORY i
            JOIN MEDICINES m ON i.medicine_id = m.medicine_id
            GROUP BY m.medicine_id
            ORDER BY total_quantity ASC
            """
            self.cursor.execute(query)
            report = self.cursor.fetchall()
            
            # Add summary statistics
            total_items = sum(item['total_quantity'] for item in report)
            expiring_soon = len([item for item in report 
                               if item['earliest_expiry'] and 
                               (item['earliest_expiry'] - datetime.now().date()).days <= 30])
            
            return {
                "report": report,
                "summary": {
                    "total_items": total_items,
                    "unique_medicines": len(report),
                    "items_expiring_soon": expiring_soon
                }
            }
        except Exception as e:
            return {"error": f"Error generating report: {str(e)}"}
        

    def delete_inventory_item(self, inventory_id):
        """Delete an inventory item by its ID"""
        try:
            # First, check if the inventory item exists
            self.cursor.execute("SELECT 1 FROM inventory WHERE inventory_id = %s", (inventory_id,))
            if not self.cursor.fetchone():
                return {"success": False, "message": f"Inventory ID {inventory_id} not found"}

            # Proceed to delete the inventory item
            self.cursor.execute("DELETE FROM inventory WHERE inventory_id = %s", (inventory_id,))
            self.conn.commit()
            return {"success": True, "message": f"Inventory ID {inventory_id} deleted successfully"}
        except mysql.connector.Error as db_error:
            self.conn.rollback()
            return {"success": False, "message": f"Database error: {db_error.msg}"}
        except Exception as e:
            self.conn.rollback()
            return {"success": False, "message": f"Unexpected error: {str(e)}"}
