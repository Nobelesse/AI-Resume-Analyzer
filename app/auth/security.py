"""Password hashing with Argon2id; never store plaintext passwords."""
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

HASHER = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)

def validate_password(password: str) -> None:
    if not isinstance(password, str) or len(password) < 12 or len(password) > 128:
        raise ValueError("Password must contain 12–128 characters.")
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one letter and one number.")

def hash_password(password: str) -> str:
    validate_password(password)
    return HASHER.hash(password)

def verify_password(encoded: str, password: str) -> bool:
    try:
        return HASHER.verify(encoded, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError, TypeError):
        return False
