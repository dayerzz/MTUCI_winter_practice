from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    motorcycles = Column(Integer, default=0)
    violations = Column(Integer, default=0)