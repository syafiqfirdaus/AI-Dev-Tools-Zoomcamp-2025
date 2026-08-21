"""
Pydantic schemas for request/response validation
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


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
    risk_free_rate: float = Field(
        ...,
        ge=-1,
        le=1,
        description="Annual risk-free rate (decimal; negative rates are supported)",
    )
    periods_per_year: int = Field(
        default=252,
        ge=1,
        le=366,
        description="Number of return observations per year",
    )


class RiskMetricsResponse(BaseModel):
    volatility: float
    sharpe_ratio: float
    average_return: float
    annualized_return: float
    max_drawdown: float
    periods_per_year: int
    observations: int
    calculation_id: str


# Derivatives Pricing Schemas
class OptionInputs(BaseModel):
    spot: float = Field(..., gt=0)
    strike: float = Field(..., gt=0)
    time_to_maturity: float = Field(..., gt=0, description="Years until expiry")
    risk_free_rate: float = Field(..., ge=-1, le=1, description="Continuously compounded rate")
    volatility: float = Field(..., gt=0, le=5, description="Annualized volatility")
    option_type: Literal["call", "put"]
    dividend_yield: float = Field(default=0, ge=-1, le=1)


class BlackScholesRequest(OptionInputs):
    pass


class BlackScholesResponse(BaseModel):
    model: str
    option_type: str
    price: float
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    calculation_id: str


class BinomialOptionRequest(OptionInputs):
    steps: int = Field(default=200, ge=1, le=2_000)
    american: bool = False


class BinomialOptionResponse(BaseModel):
    model: str
    option_type: str
    price: float
    steps: int
    american: bool
    calculation_id: str


class MonteCarloOptionRequest(OptionInputs):
    simulations: int = Field(default=50_000, ge=1_000, le=1_000_000, multiple_of=2)
    seed: int = 42


class MonteCarloOptionResponse(BaseModel):
    model: str
    option_type: str
    price: float
    standard_error: float
    confidence_interval_low: float
    confidence_interval_high: float
    simulations: int
    seed: int
    calculation_id: str


# Value-at-Risk Schemas
class ValueAtRiskRequest(BaseModel):
    returns: List[float] = Field(..., min_length=2)
    portfolio_value: float = Field(..., gt=0)
    confidence_level: float = Field(default=0.95, gt=0.5, lt=1)
    method: Literal["historical", "parametric"] = "historical"


class ValueAtRiskResponse(BaseModel):
    method: str
    confidence_level: float
    value_at_risk: float
    expected_shortfall: float
    observations: int
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
