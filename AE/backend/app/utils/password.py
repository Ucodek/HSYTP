from typing import Any, Dict

from app.core.security import get_password_hash


def handle_password_update(update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle password hashing for user updates."""
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    return update_data
