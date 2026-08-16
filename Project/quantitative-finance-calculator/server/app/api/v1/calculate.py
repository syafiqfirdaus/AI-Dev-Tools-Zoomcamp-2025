"""
API routes for financial calculations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models import Calculation
from app.schemas import (
    CompoundInterestRequest, CompoundInterestResponse,
    LoanAmortizationRequest, LoanAmortizationResponse,
    InvestmentReturnRequest, InvestmentReturnResponse,
    RiskMetricsRequest, RiskMetricsResponse
)
from app.services.finance_calculator import (
    calculate_compound_interest,
    calculate_loan_amortization,
    calculate_investment_return,
    calculate_risk_metrics
)

router = APIRouter(prefix="/api/v1/calculate", tags=["calculations"])


@router.post("/compound-interest", response_model=CompoundInterestResponse)
def compound_interest_endpoint(
    request: CompoundInterestRequest,
    db: Session = Depends(get_db)
):
    """Calculate compound interest"""
    try:
        result = calculate_compound_interest(
            principal=request.principal,
            rate=request.rate,
            time=request.time,
            compounds_per_year=request.compounds_per_year
        )
        
        # Save to database
        calculation_id = str(uuid.uuid4())
        calc = Calculation(
            id=calculation_id,
            calculation_type="compound_interest",
            input_data=request.model_dump(),
            result_data=result
        )
        db.add(calc)
        db.commit()
        
        return CompoundInterestResponse(
            **result,
            calculation_id=calculation_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/loan-amortization", response_model=LoanAmortizationResponse)
def loan_amortization_endpoint(
    request: LoanAmortizationRequest,
    db: Session = Depends(get_db)
):
    """Calculate loan amortization schedule"""
    try:
        result = calculate_loan_amortization(
            principal=request.principal,
            annual_rate=request.annual_rate,
            term_years=request.term_years
        )
        
        # Save to database
        calculation_id = str(uuid.uuid4())
        calc = Calculation(
            id=calculation_id,
            calculation_type="loan_amortization",
            input_data=request.model_dump(),
            result_data=result
        )
        db.add(calc)
        db.commit()
        
        return LoanAmortizationResponse(
            **result,
            calculation_id=calculation_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/investment-return", response_model=InvestmentReturnResponse)
def investment_return_endpoint(
    request: InvestmentReturnRequest,
    db: Session = Depends(get_db)
):
    """Calculate investment returns (ROI and CAGR)"""
    try:
        result = calculate_investment_return(
            initial_value=request.initial_value,
            final_value=request.final_value,
            years=request.years
        )
        
        # Save to database
        calculation_id = str(uuid.uuid4())
        calc = Calculation(
            id=calculation_id,
            calculation_type="investment_return",
            input_data=request.model_dump(),
            result_data=result
        )
        db.add(calc)
        db.commit()
        
        return InvestmentReturnResponse(
            **result,
            calculation_id=calculation_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/risk-metrics", response_model=RiskMetricsResponse)
def risk_metrics_endpoint(
    request: RiskMetricsRequest,
    db: Session = Depends(get_db)
):
    """Calculate portfolio risk metrics"""
    try:
        result = calculate_risk_metrics(
            returns=request.returns,
            risk_free_rate=request.risk_free_rate
        )
        
        # Save to database
        calculation_id = str(uuid.uuid4())
        calc = Calculation(
            id=calculation_id,
            calculation_type="risk_metrics",
            input_data=request.model_dump(),
            result_data=result
        )
        db.add(calc)
        db.commit()
        
        return RiskMetricsResponse(
            **result,
            calculation_id=calculation_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
