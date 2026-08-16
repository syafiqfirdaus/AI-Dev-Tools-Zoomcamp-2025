"""
API routes for calculation history
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Calculation
from app.schemas import HistoryResponse, CalculationHistory

router = APIRouter(prefix="/api/v1", tags=["history"])


@router.get("/history", response_model=HistoryResponse)
def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    calculation_type: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Get calculation history with optional filtering and pagination
    """
    # Build query
    query = db.query(Calculation)
    
    # Filter by calculation type if specified
    if calculation_type:
        query = query.filter(Calculation.calculation_type == calculation_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    calculations = query.order_by(Calculation.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to response format
    items = [CalculationHistory(**calc.to_dict()) for calc in calculations]
    
    return HistoryResponse(total=total, items=items)
