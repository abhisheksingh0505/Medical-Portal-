import hashlib
import re
from typing import Dict, Optional, Tuple

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def authenticate_user(users_db: Dict, email: str, password: str, user_type: str) -> Optional[Dict]:
    """Authenticate user login"""
    hashed_password = hash_password(password)
    users = users_db.get(f"{user_type}s", [])
    
    for user in users:
        if user['email'] == email and user['password'] == hashed_password:
            return user
    return None