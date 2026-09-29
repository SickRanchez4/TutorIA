"""Small, framework-agnostic validators shared by HTTP handlers."""
from decimal import Decimal, InvalidOperation
import re


EMAIL_PATTERN = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


def normalize_email(value: object) -> str:
    """Return a canonical email representation for comparisons and storage."""
    return str(value or '').strip().lower()


def is_valid_email(value: object) -> bool:
    """Validate a practical email shape after canonicalization."""
    email = normalize_email(value)
    return len(email) <= 254 and EMAIL_PATTERN.fullmatch(email) is not None


def parse_boolean(value: object, field_name: str) -> bool:
    """Accept JSON booleans only; avoid truthy strings such as ``"false"``."""
    if not isinstance(value, bool):
        raise ValueError(f'{field_name} debe ser boolean')
    return value


def parse_non_negative_int(value: object, field_name: str, *, allow_none: bool = False) -> int | None:
    """Parse an integer while rejecting booleans, fractions and negative values."""
    if value is None and allow_none:
        return None
    if isinstance(value, bool):
        raise ValueError(f'{field_name} debe ser un entero no negativo')
    raw_value = str(value).strip()
    try:
        parsed = int(raw_value)
    except (TypeError, ValueError) as error:
        raise ValueError(f'{field_name} debe ser un entero no negativo') from error
    if raw_value != str(parsed) or parsed < 0:
        raise ValueError(f'{field_name} debe ser un entero no negativo')
    return parsed


def parse_non_negative_decimal(value: object, field_name: str, *, allow_none: bool = False) -> Decimal | None:
    """Parse a finite, non-negative decimal value."""
    if value is None and allow_none:
        return None
    if isinstance(value, bool):
        raise ValueError(f'{field_name} debe ser un número no negativo')
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f'{field_name} debe ser un número no negativo') from error
    if not parsed.is_finite() or parsed < 0:
        raise ValueError(f'{field_name} debe ser un número no negativo')
    return parsed
