"""API routes for financial calculations."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Calculation
from app.schemas import (
    BinomialOptionRequest,
    BinomialOptionResponse,
    BlackScholesRequest,
    BlackScholesResponse,
    CompoundInterestRequest,
    CompoundInterestResponse,
    InvestmentReturnRequest,
    InvestmentReturnResponse,
    LoanAmortizationRequest,
    LoanAmortizationResponse,
    MonteCarloOptionRequest,
    MonteCarloOptionResponse,
    RiskMetricsRequest,
    RiskMetricsResponse,
    ValueAtRiskRequest,
    ValueAtRiskResponse,
)
from app.services.finance_calculator import (
    calculate_compound_interest,
    calculate_investment_return,
    calculate_loan_amortization,
    calculate_risk_metrics,
)
from app.services.quantitative_finance import (
    calculate_binomial_option,
    calculate_black_scholes,
    calculate_monte_carlo_option,
    calculate_value_at_risk,
)

router = APIRouter(prefix="/api/v1/calculate", tags=["calculations"])


@router.post("/compound-interest", response_model=CompoundInterestResponse)
def compound_interest_endpoint(request: CompoundInterestRequest, db: Session = Depends(get_db)):
    """Calculate compound interest"""
    try:
        result = calculate_compound_interest(
            principal=request.principal,
            rate=request.rate,
            time=request.time,
            compounds_per_year=request.compounds_per_year,
        )

        # Save to database
        calculation_id = str(uuid.uuid4())
        calc = Calculation(
            id=calculation_id,
            calculation_type="compound_interest",
            input_data=request.model_dump(),
            result_data=result,
        )
        db.add(calc)
        db.commit()

        return CompoundInterestResponse(**result, calculation_id=calculation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/loan-amortization", response_model=LoanAmortizationResponse)
def loan_amortization_endpoint(request: LoanAmortizationRequest, db: Session = Depends(get_db)):
    """Calculate loan amortization schedule"""
    try:
        result = calculate_loan_amortization(
            principal=request.principal,
            annual_rate=request.annual_rate,
            term_years=request.term_years,
        )

        # Save to database
        calculation_id = str(uuid.uuid4())
        calc = Calculation(
            id=calculation_id,
            calculation_type="loan_amortization",
            input_data=request.model_dump(),
            result_data=result,
        )
        db.add(calc)
        db.commit()

        return LoanAmortizationResponse(**result, calculation_id=calculation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/investment-return", response_model=InvestmentReturnResponse)
def investment_return_endpoint(request: InvestmentReturnRequest, db: Session = Depends(get_db)):
    """Calculate investment returns (ROI and CAGR)"""
    try:
        result = calculate_investment_return(
            initial_value=request.initial_value,
            final_value=request.final_value,
            years=request.years,
        )

        # Save to database
        calculation_id = str(uuid.uuid4())
        calc = Calculation(
            id=calculation_id,
            calculation_type="investment_return",
            input_data=request.model_dump(),
            result_data=result,
        )
        db.add(calc)
        db.commit()

        return InvestmentReturnResponse(**result, calculation_id=calculation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/risk-metrics", response_model=RiskMetricsResponse)
def risk_metrics_endpoint(request: RiskMetricsRequest, db: Session = Depends(get_db)):
    """Calculate portfolio risk metrics"""
    try:
        result = calculate_risk_metrics(
            returns=request.returns,
            risk_free_rate=request.risk_free_rate,
            periods_per_year=request.periods_per_year,
        )

        # Save to database
        calculation_id = str(uuid.uuid4())
        calc = Calculation(
            id=calculation_id,
            calculation_type="risk_metrics",
            input_data=request.model_dump(),
            result_data=result,
        )
        db.add(calc)
        db.commit()

        return RiskMetricsResponse(**result, calculation_id=calculation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def _save_calculation(db: Session, calculation_type: str, request: object, result: dict) -> str:
    calculation_id = str(uuid.uuid4())
    calc = Calculation(
        id=calculation_id,
        calculation_type=calculation_type,
        input_data=request.model_dump(),
        result_data=result,
    )
    db.add(calc)
    db.commit()
    return calculation_id


@router.post("/option-pricing/black-scholes", response_model=BlackScholesResponse)
def black_scholes_endpoint(request: BlackScholesRequest, db: Session = Depends(get_db)):
    """Price a European option analytically and calculate its Greeks."""
    try:
        result = calculate_black_scholes(**request.model_dump())
        calculation_id = _save_calculation(db, "black_scholes", request, result)
        return BlackScholesResponse(**result, calculation_id=calculation_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/option-pricing/binomial", response_model=BinomialOptionResponse)
def binomial_option_endpoint(request: BinomialOptionRequest, db: Session = Depends(get_db)):
    """Price a European or American option with a CRR binomial tree."""
    try:
        result = calculate_binomial_option(**request.model_dump())
        calculation_id = _save_calculation(db, "binomial_option", request, result)
        return BinomialOptionResponse(**result, calculation_id=calculation_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/option-pricing/monte-carlo", response_model=MonteCarloOptionResponse)
def monte_carlo_option_endpoint(
    request: MonteCarloOptionRequest,
    db: Session = Depends(get_db),
):
    """Price a European option with reproducible Monte Carlo simulation."""
    try:
        result = calculate_monte_carlo_option(**request.model_dump())
        calculation_id = _save_calculation(db, "monte_carlo_option", request, result)
        return MonteCarloOptionResponse(**result, calculation_id=calculation_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/value-at-risk", response_model=ValueAtRiskResponse)
def value_at_risk_endpoint(request: ValueAtRiskRequest, db: Session = Depends(get_db)):
    """Calculate one-period VaR and Expected Shortfall."""
    try:
        result = calculate_value_at_risk(**request.model_dump())
        calculation_id = _save_calculation(db, "value_at_risk", request, result)
        return ValueAtRiskResponse(**result, calculation_id=calculation_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
