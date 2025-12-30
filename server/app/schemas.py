"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


# Compound Interest Schemas
class CompoundInterestRequest(BaseModel):
    principal: float = Field(..., ge=0, description="Initial investment amount")
    rate: float = Field(..., ge=0, le=1, description="Annual interest rate (decimal)")
    time: float = Field(..., ge=0, description="Investment period in years")
    compounds_per_year: int = Field(..., ge=1, description="Compounding frequency")


class CompoundInterestResponse(BaseModel):
    future_value: float
    total_interest: float
    calculation_id: str


# Loan Amortization Schemas
class LoanAmortizationRequest(BaseModel):
    principal: float = Field(..., gt=0, description="Loan amount")
    annual_rate: float = Field(..., ge=0, le=1, description="Annual interest rate (decimal)")
    term_years: int = Field(..., ge=1, description="Loan term in years")


class PaymentPeriod(BaseModel):
    period: int
    payment: float
    principal: float
    interest: float
    balance: float


class LoanAmortizationResponse(BaseModel):
    monthly_payment: float
    total_payment: float
    total_interest: float
    amortization_schedule: List[PaymentPeriod]
    calculation_id: str


# Investment Return Schemas
class InvestmentReturnRequest(BaseModel):
    initial_value: float = Field(..., gt=0, description="Initial investment value")
    final_value: float = Field(..., ge=0, description="Final investment value")
    years: float = Field(..., gt=0, description="Investment period in years")


class InvestmentReturnResponse(BaseModel):
    roi: float
    cagr: float
    total_return: float
    calculation_id: str


# Risk Metrics Schemas
class RiskMetricsRequest(BaseModel):
    returns: List[float] = Field(..., min_length=2, description="Historical returns")
    risk_free_rate: float = Field(..., ge=0, le=1, description="Risk-free rate (decimal)")


class RiskMetricsResponse(BaseModel):
    volatility: float
    sharpe_ratio: float
    average_return: float
    calculation_id: str


# History Schemas
class CalculationHistory(BaseModel):
    id: str
    calculation_type: str
    input_data: dict
    result_data: dict
    created_at: datetime


class HistoryResponse(BaseModel):
    total: int
    items: List[CalculationHistory]


# Error Response
class ErrorResponse(BaseModel):
    error: str
    details: Optional[dict] = None
