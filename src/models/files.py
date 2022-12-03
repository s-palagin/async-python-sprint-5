from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.db import Base


class FileModel(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    path = Column(String(100))
    size = Column(Integer)
    is_downloadable = Column(Boolean)
    author = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship('UsersTable', back_populates='files')
