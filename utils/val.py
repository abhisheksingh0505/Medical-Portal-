# utils/validators.py - Input Validation Functions
import re
from typing import Tuple, List, Dict, Any

def validate_email(email: str) -> bool:
    """
    Validate email format using regex pattern
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if email format is valid, False otherwise
    """
    if not email:
        return False
    
    # RFC 5322 compliant email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength with multiple criteria
    
    Args:
        password (str): Password to validate
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    # Check minimum length
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    # Check maximum length (security best practice)
    if len(password) > 128:
        return False, "Password must be no more than 128 characters long"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"

def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format (supports various international formats)
    
    Args:
        phone (str): Phone number to validate
    
    Returns:
        bool: True if phone format is valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove all non-digit characters except + for country code
    cleaned = re.sub(r'[^\d+]', '', phone.strip())
    
    # Check for valid patterns
    patterns = [
        r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$',  # US format
        r'^\+?[1-9]\d{1,14}$',                 # International format (E.164)
    ]
    
    return any(re.match(pattern, cleaned) for pattern in patterns)

def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url (str): URL to validate
    
    Returns:
        bool: True if URL format is valid, False otherwise
    """
    if not url:
        return False
    
    # URL validation pattern
    pattern = r'^https?:\/\/(?:[-\w.])+(?:\:[0-9]+)?(?:\/(?:[\w\/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    return re.match(pattern, url.strip()) is not None

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate that all required fields are present and not empty
    
    Args:
        data (Dict[str, Any]): Dictionary containing form data
        required_fields (List[str]): List of required field names
    
    Returns:
        Tuple[bool, List[str]]: (all_valid, list_of_missing_fields)
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not data[field] or (isinstance(data[field], str) and not data[field].strip()):
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields

def validate_numeric_range(value: str, min_val: float = None, max_val: float = None) -> Tuple[bool, str]:
    """
    Validate numeric value and check if it's within specified range
    
    Args:
        value (str): String representation of numeric value
        min_val (float, optional): Minimum allowed value
        max_val (float, optional): Maximum allowed value
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not value:
        return False, "Value is required"
    
    try:
        num_value = float(value)
    except ValueError:
        return False, "Value must be a valid number"
    
    if min_val is not None and num_value < min_val:
        return False, f"Value must be at least {min_val}"
    
    if max_val is not None and num_value > max_val:
        return False, f"Value must be no more than {max_val}"
    
    return True, "Value is valid"

def sanitize_input(text: str) -> str:
    """
    Basic input sanitization to prevent XSS and other injection attacks
    
    Args:
        text (str): Input text to sanitize
    
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    sanitized = text
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()

# Example usage and testing
if __name__ == "__main__":
    # Test email validation
    print("Email validation tests:")
    emails = ["test@example.com", "invalid-email", "user@domain.co.uk"]
    for email in emails:
        print(f"{email}: {validate_email(email)}")
    
    # Test password validation
    print("\nPassword validation tests:")
    passwords = ["weak", "StrongPass1!", "nocaps123!", "NOLOWER123!"]
    for pwd in passwords:
        valid, msg = validate_password(pwd)
        print(f"{pwd}: {valid} - {msg}")
    
    # Test phone validation
    print("\nPhone validation tests:")
    phones = ["+1-555-123-4567", "555-123-4567", "invalid-phone"]
    for phone in phones:
        print(f"{phone}: {validate_phone_number(phone)}")
    
    # Test required fields validation
    print("\nRequired fields validation test:")
    form_data = {"username": "john", "email": "john@example.com", "password": ""}
    required = ["username", "email", "password"]
    valid, missing = validate_required_fields(form_data, required)
    print(f"Valid: {valid}, Missing: {missing}")