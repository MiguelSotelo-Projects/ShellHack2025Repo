# Common utilities and base classes for models
from datetime import datetime
from typing import Optional


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


def generate_confirmation_code() -> str:
    """Generate a confirmation code for appointments"""
    import random
    import string
    
    # Generate format: ABCD-1234
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    numbers = ''.join(random.choices(string.digits, k=4))
    return f"{letters}-{numbers}"


def generate_ticket_number() -> str:
    """Generate a ticket number for queue entries"""
    import random
    import string
    
    # Generate format: C-1234 (C for Check-in)
    number = ''.join(random.choices(string.digits, k=4))
    return f"C-{number}"

