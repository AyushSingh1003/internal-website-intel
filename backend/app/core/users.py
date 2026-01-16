from typing import Optional
from app.core.security import verify_password, get_password_hash

# Hardcoded users (username: hashed_password)
# Default password for all users: "password123"
USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("password123"),
        "full_name": "Admin User"
    },
    "demo": {
        "username": "demo",
        "hashed_password": get_password_hash("password123"),
        "full_name": "Demo User"
    }
}


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user with username and password"""
    user = USERS_DB.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user
