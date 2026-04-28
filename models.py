from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from database import Base

class Advertisement(Base):
    __tablename__ = 'advertisement'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    author = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)