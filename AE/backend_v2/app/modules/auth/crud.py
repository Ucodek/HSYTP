import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.modules.auth.models import Token, TokenType, User, UserRole
from app.modules.auth.schemas import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email_or_username(db: Session, identifier: str) -> Optional[User]:
    """Get a user by email or username."""
    return (
        db.query(User)
        .filter(or_(User.email == identifier, User.username == identifier))
        .first()
    )


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    role: Optional[UserRole] = None,
) -> List[User]:
    """Get a filtered list of users with pagination."""
    query = db.query(User)

    # Apply filters if provided
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if role is not None:
        query = query.filter(User.role == role)

    # Apply pagination
    return query.offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    try:
        # Hash the password
        hashed_password = get_password_hash(user.password)

        # Create the user object
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )

        # Add to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"Created user with username: {user.username}")
        return db_user

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update a user by ID."""
    user = get_user(db, user_id)
    if not user:
        return None

    try:
        # Extract only provided fields
        update_data = user_update.model_dump(exclude_unset=True)

        # Handle password separately
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        # Check email uniqueness if being updated
        if "email" in update_data and update_data["email"] != user.email:
            existing_user = get_user_by_email(db, update_data["email"])
            if existing_user:
                logger.warning(f"Cannot update user {user_id}: email already exists")
                return None

        # Check username uniqueness if being updated
        if "username" in update_data and update_data["username"] != user.username:
            existing_user = get_user_by_username(db, update_data["username"])
            if existing_user:
                logger.warning(f"Cannot update user {user_id}: username already exists")
                return None

        # Update user attributes
        for field, value in update_data.items():
            setattr(user, field, value)

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"Updated user ID: {user_id}")
        return user

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user: {str(e)}")
        raise


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user by ID."""
    user = get_user(db, user_id)
    if not user:
        return False

    try:
        db.delete(user)
        db.commit()
        logger.info(f"Deleted user ID: {user_id}")
        return True

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        raise


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user with username/email and password."""
    # We should use get_user_by_email_or_username to be consistent
    user = get_user_by_email_or_username(db, username)

    # Check if user exists and password is correct
    if not user or not verify_password(password, user.hashed_password):
        return None

    return user


def change_password(db: Session, user: User, new_password: str) -> User:
    """Change a user's password."""
    try:
        # Hash the new password
        user.hashed_password = get_password_hash(new_password)

        # Revoke existing tokens for security
        revoke_all_user_tokens(db, user.id)

        # Save changes
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"Changed password for user ID: {user.id}")
        return user

    except Exception as e:
        db.rollback()
        logger.error(f"Error changing password: {str(e)}")
        raise


# Token CRUD operations
def create_token(
    db: Session,
    user_id: int,
    token: str,
    token_type: TokenType,
    expires_delta: Optional[timedelta] = None,
) -> Token:
    """Create a new token."""
    try:
        # Set expiration time - ensure we use timezone.utc to match the model's is_expired
        expires_at = datetime.now(timezone.utc)

        if expires_delta:
            expires_at += expires_delta
        else:
            # Default expiration times based on token type
            if token_type == TokenType.ACCESS:
                expires_at += timedelta(minutes=30)
            elif token_type == TokenType.REFRESH:
                expires_at += timedelta(days=7)
            elif token_type == TokenType.RESET_PASSWORD:
                expires_at += timedelta(hours=24)
            elif token_type == TokenType.VERIFY_EMAIL:
                expires_at += timedelta(days=3)
            else:
                expires_at += timedelta(hours=1)  # Default fallback

        # Create token
        db_token = Token(
            token=token,
            token_type=token_type,
            expires_at=expires_at,
            user_id=user_id,
        )

        db.add(db_token)
        db.commit()
        db.refresh(db_token)

        return db_token

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating token: {str(e)}")
        raise


def get_token(db: Session, token: str, token_type: TokenType) -> Optional[Token]:
    """Get a token by value and type."""
    return (
        db.query(Token)
        .filter(Token.token == token, Token.token_type == token_type)
        .first()
    )


def get_valid_token(db: Session, token: str, token_type: TokenType) -> Optional[Token]:
    """Get a valid (non-expired, non-revoked) token."""
    # Use the Token model's is_expired and is_valid properties instead of reinventing
    tokens = (
        db.query(Token)
        .filter(
            Token.token == token,
            Token.token_type == token_type,
        )
        .all()
    )

    # Find first valid token
    for token in tokens:
        if token.is_valid:
            return token

    return None


def revoke_token(db: Session, token: Token) -> Token:
    """Revoke a token."""
    try:
        token.is_revoked = True
        db.add(token)
        db.commit()
        db.refresh(token)

        logger.info(f"Revoked {token.token_type} token for user ID: {token.user_id}")
        return token

    except Exception as e:
        db.rollback()
        logger.error(f"Error revoking token: {str(e)}")
        raise


def revoke_all_user_tokens(
    db: Session, user_id: int, token_type: Optional[TokenType] = None
) -> int:
    """
    Revoke all tokens for a user.

    Returns the number of tokens revoked.
    """
    try:
        query = db.query(Token).filter(
            Token.user_id == user_id, Token.is_revoked == False
        )

        if token_type:
            query = query.filter(Token.token_type == token_type)

        tokens = query.all()
        count = 0

        for token in tokens:
            token.is_revoked = True
            db.add(token)
            count += 1

        db.commit()

        if count > 0:
            logger.info(f"Revoked {count} tokens for user ID: {user_id}")

        return count

    except Exception as e:
        db.rollback()
        logger.error(f"Error revoking user tokens: {str(e)}")
        raise


def cleanup_expired_tokens(db: Session) -> int:
    """
    Delete expired tokens to maintain database performance.

    Returns the number of tokens deleted.
    """
    try:
        now = datetime.now(timezone.utc)
        expired_tokens = db.query(Token).filter(Token.expires_at < now).all()

        count = len(expired_tokens)

        for token in expired_tokens:
            db.delete(token)

        db.commit()

        if count > 0:
            logger.info(f"Cleaned up {count} expired tokens")

        return count

    except Exception as e:
        db.rollback()
        logger.error(f"Error cleaning up tokens: {str(e)}")
        raise


def get_active_tokens(
    db: Session, user_id: int, token_type: Optional[TokenType] = None
) -> List[Token]:
    """Get all active (non-expired, non-revoked) tokens for a user."""
    now = datetime.now(timezone.utc)

    query = db.query(Token).filter(
        Token.user_id == user_id, Token.is_revoked == False, Token.expires_at > now
    )

    if token_type:
        query = query.filter(Token.token_type == token_type)

    return query.all()
