from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.db import Base


class UsersTable(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, index=True)
    hashed_password = Column(String())
    is_active = Column(
        Boolean(),
        default=True,
        nullable=False,
    )
    tokens = relationship(
        'TokensTable', back_populates="user", passive_deletes=True
    )
    files = relationship(
        'FileModel', back_populates="user", passive_deletes=True
    )


class TokensTable(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True)
    token = Column(
        UUID(as_uuid=False),
        server_default=text("uuid_generate_v4()"),
        unique=True,
        nullable=False,
        index=True,
    )
    expires = Column(DateTime())
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship('UsersTable', back_populates='tokens')
