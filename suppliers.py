from database import get_db_connection
import re
from medicines import Medicine

class SupplierManager:
    def __init__(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def _get_next_supplier_id(self):
        """Manually get the next available supplier ID"""
        self.cursor.execute("SELECT MAX(supplier_id) FROM suppliers")
        result = self.cursor.fetchone()
        return (result['MAX(supplier_id)'] or 0) + 1

    # Validation helpers
    def _validate_phone(self, phone):
        """Validate phone number format"""
        return re.match(r'^\+?[\d\s-]{10,15}$', phone) is not None

    def _validate_email(self, email):
        """Validate email format"""
        return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

    # New helper method
    def get_supplier_id_by_email(self, email):
        """Get supplier ID by email"""
        try:
            self.cursor.execute("SELECT supplier_id FROM suppliers WHERE email = %s", (email,))
            result = self.cursor.fetchone()
            return result['supplier_id'] if result else None
        except Exception as e:
            print(f"Error getting supplier ID: {str(e)}")
            return None

    # Core Supplier Functions
    def add_supplier(self, name, phone, email, address):
        """Add a new supplier with validation and manual ID generation"""
        try:
            # Validate inputs
            if not self._validate_phone(phone):
                return {"success": False, "message": "Invalid phone number format"}
            
            if not self._validate_email(email):
                return {"success": False, "message": "Invalid email format"}
            
            # Check for duplicate phone or email
            self.cursor.execute("SELECT supplier_id FROM suppliers WHERE phone = %s OR email = %s", 
                              (phone, email))
            if self.cursor.fetchone():
                return {"success": False, "message": "Supplier with this phone or email already exists"}
            
            # Generate new supplier ID
            supplier_id = self._get_next_supplier_id()
            
            # Insert new supplier with manual ID
            query = """
            INSERT INTO suppliers (supplier_id, name, phone, email, address)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (supplier_id, name, phone, email, address))
            self.conn.commit()
            return {"success": True, "message": "Supplier added successfully", 
                   "supplier_id": supplier_id}
        except Exception as e:
            self.conn.rollback()
            return {"success": False, "message": f"Error adding supplier: {str(e)}"}

    def update_supplier(self, identifier, name=None, phone=None, email=None, address=None):
        """Update supplier information with validation (can use ID or email)"""
        try:
            # Determine if identifier is ID or email
            if isinstance(identifier, int) or identifier.isdigit():
                supplier_id = int(identifier)
            else:
                supplier_id = self.get_supplier_id_by_email(identifier)
                if not supplier_id:
                    return {"success": False, "message": "Supplier not found"}

            # Build dynamic update query
            updates = []
            params = []
            
            if name:
                updates.append("name = %s")
                params.append(name)
            
            if phone:
                if not self._validate_phone(phone):
                    return {"success": False, "message": "Invalid phone number format"}
                updates.append("phone = %s")
                params.append(phone)
            
            if email:
                if not self._validate_email(email):
                    return {"success": False, "message": "Invalid email format"}
                updates.append("email = %s")
                params.append(email)
            
            if address:
                updates.append("address = %s")
                params.append(address)
            
            if not updates:
                return {"success": False, "message": "No fields to update"}
            
            # Check for duplicate phone or email
            if phone or email:
                check_query = "SELECT supplier_id FROM suppliers WHERE supplier_id != %s AND ("
                check_params = [supplier_id]
                conditions = []
                
                if phone:
                    conditions.append("phone = %s")
                    check_params.append(phone)
                if email:
                    conditions.append("email = %s")
                    check_params.append(email)
                
                check_query += " OR ".join(conditions) + ")"
                self.cursor.execute(check_query, check_params)
                if self.cursor.fetchone():
                    return {"success": False, "message": "Another supplier with this phone or email already exists"}
            
            # Perform update
            query = f"UPDATE suppliers SET {', '.join(updates)} WHERE supplier_id = %s"
            params.append(supplier_id)
            self.cursor.execute(query, params)
            self.conn.commit()
            
            return {"success": True, "message": "Supplier updated successfully"}
        except Exception as e:
            self.conn.rollback()
            return {"success": False, "message": f"Error updating supplier: {str(e)}"}

    def get_supplier_by_id_or_email(self, identifier):
        """Get supplier details by ID or email"""
        try:
            if isinstance(identifier, int) or identifier.isdigit():
                query = "SELECT * FROM suppliers WHERE supplier_id = %s"
            else:
                query = "SELECT * FROM suppliers WHERE email = %s"
            
            self.cursor.execute(query, (identifier,))
            supplier = self.cursor.fetchone()
            if not supplier:
                return {"success": False, "message": "Supplier not found"}
            return {"success": True, "supplier": supplier}
        except Exception as e:
            return {"success": False, "message": f"Error fetching supplier: {str(e)}"}

    def search_suppliers(self, search_term):
        """Search suppliers by name, phone, or email"""
        try:
            query = """
            SELECT * FROM suppliers 
            WHERE name LIKE %s OR phone LIKE %s OR email LIKE %s
            ORDER BY name
            """
            search_pattern = f"%{search_term}%"
            self.cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            return self.cursor.fetchall()
        except Exception as e:
            return {"error": f"Error searching suppliers: {str(e)}"}

    

    def get_top_suppliers(self, limit=5):
        """Get top suppliers by inventory volume"""
        try:
            query = """
            SELECT 
                s.supplier_id, 
                s.name, 
                COUNT(i.inventory_id) as item_count, 
                SUM(i.current_quantity) as total_quantity
            FROM suppliers s
            LEFT JOIN inventory i ON s.supplier_id = i.supplier_id
            GROUP BY s.supplier_id, s.name
            ORDER BY total_quantity DESC
            LIMIT %s
            """
            self.cursor.execute(query, (limit,))
            suppliers = self.cursor.fetchall()
            
            # Convert None to 0 for suppliers with no inventory
            for supplier in suppliers:
                if supplier['total_quantity'] is None:
                    supplier['total_quantity'] = 0
                if supplier['item_count'] is None:
                    supplier['item_count'] = 0
            
            return suppliers
        except Exception as e:
            return {"error": f"Error fetching top suppliers: {str(e)}"}

    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()


    def get_supplier_inventory(self, supplier_id):
        """Get inventory items from a specific supplier with expiry information"""
        try:
            query = """
            SELECT 
            i.inventory_id,
            m.name AS medicine_name,
            i.batch_number,
            i.current_quantity,
            i.expiry_date,
            DATEDIFF(i.expiry_date, CURDATE()) AS days_until_expiry,
            i.location
            FROM 
            INVENTORY i
            JOIN 
            MEDICINES m ON i.medicine_id = m.medicine_id
            WHERE 
            i.supplier_id = %s
            AND i.current_quantity > 0
            ORDER BY 
            i.expiry_date, m.name
            """
            self.cursor.execute(query, (supplier_id,))
            inventory = self.cursor.fetchall()
        
            return {
            "success": True,
            "inventory": inventory,
            "message": "No inventory found" if not inventory else None
            }
        
            return {
            "success": True,
            "inventory": inventory
            }
        except Exception as e:
            return {
            "success": False,
            "error": f"Error fetching supplier inventory: {str(e)}"
            }


    

