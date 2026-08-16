"""
Database models for calculation history
"""
from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Calculation(Base):
    """
    Model to store calculation history
    """
    __tablename__ = "calculations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    calculation_type = Column(String, nullable=False, index=True)
    input_data = Column(JSON, nullable=False)
    result_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "calculation_type": self.calculation_type,
            "input_data": self.input_data,
            "result_data": self.result_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
