"""Favorites migration utility (G19)."""

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.models import Favorite, User
from app.core.logging import logger


def migrate_favorites_from_session(
    db: Session, user: User, session_id: str
) -> int:
    """
    Migrate favorites from session-based (user_id VARCHAR) to user-based (user_id INTEGER).

    Args:
        db: Database session
        user: User model instance
        session_id: Session ID from cookie (VARCHAR user_id in favorites table)

    Returns:
        Number of favorites migrated
    """
    if not session_id:
        logger.debug("No session_id provided, skipping favorites migration")
        return 0

    try:
        # Check if user_id_new column exists (migration schema prepared)
        # If not, this migration will be skipped (schema not migrated yet)
        result = db.execute(
            text(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'favorites' 
                AND column_name = 'user_id_new'
                """
            )
        )
        if not result.fetchone():
            logger.debug(
                "user_id_new column not found, skipping favorites migration (schema not migrated)"
            )
            return 0

        # Find all favorites with session_id (old user_id VARCHAR)
        session_favorites = (
            db.query(Favorite)
            .filter(Favorite.user_id == session_id)
            .all()
        )

        if not session_favorites:
            logger.debug("No session-based favorites found", session_id=session_id[:8])
            return 0

        # Check if user already has favorites (migration already done)
        existing_count = db.execute(
            text(
                """
                SELECT COUNT(*) 
                FROM favorites 
                WHERE user_id_new = :user_id
                """
            ),
            {"user_id": user.id},
        ).scalar()

        if existing_count > 0:
            logger.debug(
                "User already has favorites, skipping migration",
                user_id=user.id,
                existing_count=existing_count,
            )
            return 0

        # Migrate favorites: update user_id_new column
        migrated_count = 0
        for favorite in session_favorites:
            # Update user_id_new column (raw SQL to avoid model issues)
            db.execute(
                text(
                    """
                    UPDATE favorites 
                    SET user_id_new = :user_id 
                    WHERE id = :favorite_id
                    """
                ),
                {"user_id": user.id, "favorite_id": favorite.id},
            )
            migrated_count += 1

        db.commit()

        logger.info(
            "Favorites migrated successfully",
            user_id=user.id,
            session_id=session_id[:8],
            migrated_count=migrated_count,
        )

        return migrated_count

    except Exception as e:
        logger.error(
            "Failed to migrate favorites",
            error=str(e),
            user_id=user.id,
            session_id=session_id[:8] if session_id else None,
        )
        db.rollback()
        return 0

