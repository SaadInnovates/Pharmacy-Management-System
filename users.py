from database import get_db_connection
import re

class UserManager:
    def __init__(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor(dictionary=True)
        self._current_user = None 


    def set_current_user(self, user):
        self._current_user = user

    def get_current_user(self):
        return self._current_user

    # Validation helpers
    def _validate_phone(self, phone):
        """Validate phone number format"""
        return re.match(r'^\+?[\d\s-]{10,15}$', phone) is not None

    def _validate_email(self, email):
        """Validate email format"""
        return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

    def _validate_password(self, password):
        """Validate password requirements (but won't encrypt)"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        return True

    def _hash_password(self, password):
        """No longer hashes password, just returns as-is"""
        return password

    def _check_password(self, password, stored_password):
        """Simple plaintext password comparison"""
        return password == stored_password

    
    def authenticate_user(self, email, password):
        """Authenticate user with plaintext password"""
        try:
            if not email or not password:
                return {"success": False, "message": "Email and password are required"}

            password = password.strip()
            email = email.strip()

            query = "SELECT * FROM USERS WHERE email = %s"
            self.cursor.execute(query, (email,))
            user = self.cursor.fetchone()

            if not user:
                return {"success": False, "message": "Invalid credentials"}

            stored_password = user['password']

            # Simple password comparison
            if password != stored_password:
                return {"success": False, "message": "Invalid credentials"}

            user_data = {k: v for k, v in user.items() if k != 'password'}
            return {"success": True, "user": user_data}

        except Exception as e:
            return {"success": False, "message": f"Authentication error: {str(e)}"}

    def update_user(self, user_id, name=None, email=None, phone=None, role=None, password=None):
        """Update user information with validation"""
        try:
            updates = []
            params = []
            
            if name:
                updates.append("name = %s")
                params.append(name)
            
            if email:
                if not self._validate_email(email):
                    return {"success": False, "message": "Invalid email format"}
                updates.append("email = %s")
                params.append(email)
            
            if phone:
                if not self._validate_phone(phone):
                    return {"success": False, "message": "Invalid phone number format"}
                updates.append("phone = %s")
                params.append(phone)
            
            if role:
                updates.append("role = %s")
                params.append(role)
            
            if password:
                if not self._validate_password(password):
                    return {"success": False, "message": "Password must be at least 8 characters with uppercase, lowercase, and numbers"}
                updates.append("password = %s")
                params.append(password)
            
            if not updates:
                return {"success": False, "message": "No fields to update"}
            
            # Check for duplicate email or phone
            if email or phone:
                check_query = "SELECT user_id FROM USERS WHERE user_id != %s AND ("
                check_params = [user_id]
                conditions = []
                
                if email:
                    conditions.append("email = %s")
                    check_params.append(email)
                if phone:
                    conditions.append("phone = %s")
                    check_params.append(phone)
                
                check_query += " OR ".join(conditions) + ")"
                self.cursor.execute(check_query, check_params)
                if self.cursor.fetchone():
                    return {"success": False, "message": "Another user with this email or phone already exists"}
            
            # Perform update
            query = f"UPDATE USERS SET {', '.join(updates)} WHERE user_id = %s"
            params.append(user_id)
            self.cursor.execute(query, params)
            self.conn.commit()
            
            return {"success": True, "message": "User updated successfully"}
        except Exception as e:
            self.conn.rollback()
            return {"success": False, "message": f"Error updating user: {str(e)}"}

    # User Query Functions (remain unchanged)
    def get_user_by_id(self, user_id):
        """Get user details by ID (excluding password)"""
        try:
            query = "SELECT user_id, name, email, phone, role FROM USERS WHERE user_id = %s"
            self.cursor.execute(query, (user_id,))
            user = self.cursor.fetchone()
            if not user:
                return {"success": False, "message": "User not found"}
            return {"success": True, "user": user}
        except Exception as e:
            return {"success": False, "message": f"Error fetching user: {str(e)}"}

    def get_all_users(self, role_filter=None):
        """Get all users with optional role filter"""
        try:
            query = "SELECT user_id, name, email, phone, role FROM USERS"
            params = []
            
            if role_filter:
                query += " WHERE role = %s"
                params.append(role_filter)
            
            query += " ORDER BY name"
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            return {"error": f"Error fetching users: {str(e)}"}

    def reset_password(self, email, new_password):
        """Reset user password without encryption"""
        try:
            if not self._validate_password(new_password):
                return {"success": False, "message": "Password must be at least 8 characters with uppercase, lowercase, and numbers"}
            
            query = "UPDATE USERS SET password = %s WHERE email = %s"
            self.cursor.execute(query, (new_password, email))
            self.conn.commit()
            
            if self.cursor.rowcount == 0:
                return {"success": False, "message": "User not found"}
            
            return {"success": True, "message": "Password reset successfully"}
        except Exception as e:
            self.conn.rollback()
            return {"success": False, "message": f"Error resetting password: {str(e)}"}

    def delete_user(self, user_id):
        """Delete a user account"""
        try:
            query = "DELETE FROM USERS WHERE user_id = %s"
            self.cursor.execute(query, (user_id,))
            self.conn.commit()
            
            if self.cursor.rowcount == 0:
                return {"success": False, "message": "User not found"}
            
            return {"success": True, "message": "User deleted successfully"}
        except Exception as e:
            self.conn.rollback()
            return {"success": False, "message": f"Error deleting user: {str(e)}"}

    def __del__(self):
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
            
        except Exception as e:
            pass  # Optional: log this error if you want


    def register_user(self, name, email, phone, role, password):
        """Register a new user with validation (plaintext password)"""
        try:
            # Validate inputs
            if not name or not email or not phone or not role or not password:
               return {"success": False, "message": "All fields are required"}
        
            if not self._validate_phone(phone):
               return {"success": False, "message": "Invalid phone number format"}
            if not self._validate_email(email):
               return {"success": False, "message": "Invalid email format"}
            if not self._validate_password(password):
               return {"success": False, "message": "Password must be 8+ chars with uppercase, lowercase, and numbers"}

            # Check for duplicate email or phone
            self.cursor.execute("SELECT user_id FROM USERS WHERE email = %s OR phone = %s", 
            (email, phone))
            if self.cursor.fetchone():
               return {"success": False, "message": "User with this email or phone already exists"}

            # Get the next available user_id
            self.cursor.execute("SELECT MAX(user_id) AS max_id FROM USERS")
            result = self.cursor.fetchone()
            user_id = 1 if result['max_id'] is None else result['max_id'] + 1

            # Insert new user with the generated user_id
            query = """
            INSERT INTO USERS (user_id, name, email, phone, role, password)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (user_id, name, email, phone, role, password))
            self.conn.commit()
    
            return {
            "success": True, 
            "message": "User registered successfully", 
            "user_id": user_id
            }
    
        except Exception as e:
            self.conn.rollback()
            return {
                "success": False, 
                "message": f"Error registering user: {str(e)}"
            }