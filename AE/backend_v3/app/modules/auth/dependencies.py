"""
Dependency injection setup for the authentication module.

Provides dependencies for AuthService and current user extraction.
"""

from fastapi import Depends
from fastcore.db.manager import get_db
from fastcore.security.dependencies import get_current_user_dependency

from .service import AuthService


def get_auth_service(session=Depends(get_db)):
    """
    Dependency to provide an AuthService instance with a database session.

    Args:
        session: The database session dependency.

    Returns:
        AuthService: An instance of the AuthService class.
    """
    return AuthService(session)


get_current_user = get_current_user_dependency(get_auth_service)
