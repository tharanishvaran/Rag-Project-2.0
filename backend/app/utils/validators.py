import re


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    Returns (is_valid: bool, error_message: str)
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long.'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter.'
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter.'
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one digit.'
    return True, ''


def validate_name(name: str) -> tuple[bool, str]:
    """Validate user name."""
    name = name.strip()
    if len(name) < 2:
        return False, 'Name must be at least 2 characters long.'
    if len(name) > 100:
        return False, 'Name must be 100 characters or less.'
    return True, ''
