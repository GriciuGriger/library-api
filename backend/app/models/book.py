from sqlalchemy import Column, Integer, String, Boolean
from datetime import datetime
from app.db import Base

class Book(Base):
    __tablename__ = "books"

    serial = Column(String(6), primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    is_borrowed = Column(Boolean, default=False)
    borrowed_by = Column(String(6), nullable=True)
    borrowed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Book(serial={self.serial}, title={self.title}, author={self.author})>"