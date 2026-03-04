# SRP: Password hashing is the sole responsibility of this service.
# Previously this logic lived inside auth_service.py alongside session
# management and user registration, violating SRP.
import hashlib
import hmac
import secrets


class PasswordService:
    """Handles all password-related cryptographic operations."""

    def generate_salt(self) -> str:
        return secrets.token_hex(16)

    def hash_password(self, password: str, salt_hex: str) -> str:
        salt = bytes.fromhex(salt_hex)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return digest.hex()

    def verify_password(self, password: str, salt_hex: str, expected_hash: str) -> bool:
        computed = self.hash_password(password, salt_hex)
        return hmac.compare_digest(computed, expected_hash)
