import re


def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$"
    return bool(re.match(pattern, email.lower()))


def is_strong_password(pw: str) -> bool:
    """At least 8 chars, one digit, one letter."""
    return len(pw) >= 8 and any(c.isdigit() for c in pw) and any(c.isalpha() for c in pw)


def require_fields(data: dict, fields: list) -> list:
    """Return list of missing field names."""
    return [f for f in fields if not data.get(f)]
