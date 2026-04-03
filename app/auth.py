# This file handles two things: password security and login tokens.
# It's the core of "proving who you are" in this app.

import hashlib
import secrets

# This acts as our in-memory token store.
# When a user logs in, their token is saved here along with their user ID and role.
# Format: { "abc123token": {"user_id": 1, "role": "admin"} }
# Note: this resets every time the server restarts — tokens don't survive a reboot.
active_tokens: dict = {}


def hash_password(password: str) -> str:
    # We never store passwords as plain text.
    # SHA-256 converts the password into a fixed-length string that can't be reversed.
    # So even if the database is leaked, passwords stay safe.
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    # To check a password, we hash what the user typed and compare it to the stored hash.
    # If they match, the password is correct — we never "decode" the stored hash.
    return hash_password(plain) == hashed


def create_token(user_id: int, role: str) -> str:
    # Generate a random 64-character hex string as the token.
    # secrets.token_hex is cryptographically secure — it's not guessable.
    # We then store it in active_tokens so we can look it up on future requests.
    token = secrets.token_hex(32)
    active_tokens[token] = {"user_id": user_id, "role": role}
    return token


def get_token_data(token: str) -> dict | None:
    # Look up the token and return the user info attached to it.
    # Returns None if the token doesn't exist or has been revoked.
    return active_tokens.get(token)


def revoke_token(token: str):
    # Removes the token from the store — effectively logging the user out.
    # pop with a default of None means it won't crash if the token is already gone.
    active_tokens.pop(token, None)
