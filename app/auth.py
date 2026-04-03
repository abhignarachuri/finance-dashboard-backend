import hashlib
import secrets

active_tokens: dict = {}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


def create_token(user_id: int, role: str) -> str:
    token = secrets.token_hex(32)
    active_tokens[token] = {"user_id": user_id, "role": role}
    return token


def get_token_data(token: str) -> dict | None:
    return active_tokens.get(token)


def revoke_token(token: str):
    # Removes the token from the store — effectively logging the user out.
    # pop with a default of None means it won't crash if the token is already gone.
    active_tokens.pop(token, None)
