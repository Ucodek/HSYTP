from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_refresh_token
from app.crud.base import CRUDBase
from app.models.users import RefreshToken
from app.schemas.users import RefreshTokenCreate


class CRUDToken(CRUDBase[RefreshToken, RefreshTokenCreate, RefreshTokenCreate]):
    async def create_refresh_token(
        self, db: AsyncSession, *, user_id: int
    ) -> RefreshToken:
        """Create a new refresh token for a user."""
        # Generate a secure token
        token_str = create_refresh_token()

        # Set expiration time - use timezone-aware datetime.now(timezone.utc)
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        # Create token in DB
        refresh_token = RefreshToken(
            token=token_str, user_id=user_id, expires_at=expires_at
        )

        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)
        return refresh_token

    async def get_by_token(
        self, db: AsyncSession, *, token: str
    ) -> Optional[RefreshToken]:
        """Get a refresh token by its value."""
        query = select(self.model).where(self.model.token == token)
        result = await db.execute(query)
        return result.scalars().first()

    async def revoke(self, db: AsyncSession, *, token_id: int) -> bool:
        """Revoke a refresh token."""
        query = select(self.model).where(self.model.id == token_id)
        result = await db.execute(query)
        token = result.scalars().first()

        if not token:
            return False

        token.is_revoked = True
        db.add(token)
        await db.commit()
        return True

    async def revoke_by_user(self, db: AsyncSession, *, user_id: int) -> bool:
        """Revoke all refresh tokens for a user."""
        query = select(self.model).where(self.model.user_id == user_id)
        result = await db.execute(query)
        tokens = result.scalars().all()

        for token in tokens:
            token.is_revoked = True
            db.add(token)

        await db.commit()
        return True


# Create a singleton instance
token = CRUDToken(RefreshToken)
