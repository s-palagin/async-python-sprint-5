from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from db.db import Base


class FileModel(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    path = Column(String)
    size = Column(Integer)
    is_downloadable = Column(Boolean)
    author = Column(ForeignKey("users.id", ondelete="CASCADE"))
