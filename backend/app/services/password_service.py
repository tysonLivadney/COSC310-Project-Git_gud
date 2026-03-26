import hashlib
import hmac
import secrets

PASSWORD_HASH_ITERATIONS = 100_000


def generate_salt() -> str:
    return secrets.token_hex(16)


def hash_password(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS
    )
    return digest.hex()


def verify_password(password: str, salt_hex: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password, salt_hex), expected_hash)
