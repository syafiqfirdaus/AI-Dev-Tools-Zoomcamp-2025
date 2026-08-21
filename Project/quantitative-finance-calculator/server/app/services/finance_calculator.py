"""
Financial calculation service - Pure calculation functions
"""

import math
from typing import Dict, List


def calculate_compound_interest(
    principal: float, rate: float, time: float, compounds_per_year: int
) -> Dict[str, float]:
    """
    Calculate compound interest

    Formula: FV = P × (1 + r/n)^(n×t)

    Args:
        principal: Initial investment amount
        rate: Annual interest rate (as decimal)
        time: Investment period in years
        compounds_per_year: Number of times interest is compounded per year

    Returns:
        Dictionary with future_value and total_interest
    """
    if principal < 0:
        raise ValueError("Principal must be non-negative")
    if rate < 0:
        raise ValueError("Interest rate must be non-negative")
    if time < 0:
        raise ValueError("Time must be non-negative")
    if compounds_per_year < 1:
        raise ValueError("Compounds per year must be at least 1")

    future_value = principal * (1 + rate / compounds_per_year) ** (compounds_per_year * time)
    total_interest = future_value - principal

    return {"future_value": round(future_value, 2), "total_interest": round(total_interest, 2)}


def calculate_loan_amortization(principal: float, annual_rate: float, term_years: int) -> Dict:
    """
    Calculate loan amortization schedule

    Monthly Payment Formula: M = P × [r(1+r)^n] / [(1+r)^n - 1]

    Args:
        principal: Loan amount
        annual_rate: Annual interest rate (as decimal)
        term_years: Loan term in years

    Returns:
        Dictionary with monthly_payment, total_payment, total_interest, and schedule
    """
    if principal <= 0:
        raise ValueError("Principal must be positive")
    if annual_rate < 0:
        raise ValueError("Annual rate must be non-negative")
    if term_years <= 0:
        raise ValueError("Term must be positive")

    monthly_rate = annual_rate / 12
    num_payments = term_years * 12

    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = (
            principal
            * (monthly_rate * (1 + monthly_rate) ** num_payments)
            / ((1 + monthly_rate) ** num_payments - 1)
        )

    # Generate amortization schedule
    schedule = []
    balance = principal

    for period in range(1, num_payments + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment

        schedule.append(
            {
                "period": period,
                "payment": round(monthly_payment, 2),
                "principal": round(principal_payment, 2),
                "interest": round(interest_payment, 2),
                "balance": round(max(0, balance), 2),  # Avoid negative due to rounding
            }
        )

    total_payment = monthly_payment * num_payments
    total_interest = total_payment - principal

    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "amortization_schedule": schedule,
    }


def calculate_investment_return(
    initial_value: float, final_value: float, years: float
) -> Dict[str, float]:
    """
    Calculate investment returns (ROI and CAGR)

    ROI = (Final Value - Initial Value) / Initial Value × 100
    CAGR = (Final Value / Initial Value)^(1/years) - 1

    Args:
        initial_value: Initial investment value
        final_value: Final investment value
        years: Investment period in years

    Returns:
        Dictionary with roi, cagr, and total_return
    """
    if initial_value <= 0:
        raise ValueError("Initial value must be positive")
    if final_value < 0:
        raise ValueError("Final value must be non-negative")
    if years <= 0:
        raise ValueError("Years must be positive")

    total_return = final_value - initial_value
    roi = (total_return / initial_value) * 100
    cagr = (math.pow(final_value / initial_value, 1 / years) - 1) * 100

    return {"roi": round(roi, 2), "cagr": round(cagr, 2), "total_return": round(total_return, 2)}


def calculate_risk_metrics(
    returns: List[float],
    risk_free_rate: float,
    periods_per_year: int = 252,
) -> Dict[str, float | int]:
    """
    Calculate portfolio risk metrics (volatility and Sharpe ratio)

    Volatility = Standard Deviation × sqrt(252) for annualized
    Sharpe Ratio = (Average Return - Risk-free Rate) / Volatility

    Args:
        returns: List of historical returns (as decimals)
        risk_free_rate: Annual risk-free rate (as decimal; may be negative)
        periods_per_year: Frequency used to annualize the periodic returns

    Returns:
        Dictionary with volatility, sharpe_ratio, and average_return
    """
    if len(returns) < 2:
        raise ValueError("At least 2 return values required")
    if periods_per_year < 1:
        raise ValueError("Periods per year must be at least 1")

    # Calculate average return
    avg_return = sum(returns) / len(returns)

    # Calculate variance and standard deviation
    variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
    std_dev = math.sqrt(variance)

    annualized_volatility = std_dev * math.sqrt(periods_per_year)
    annualized_return = avg_return * periods_per_year

    # Sharpe ratio
    if annualized_volatility == 0:
        sharpe_ratio = 0
    else:
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility

    wealth = 1.0
    peak = 1.0
    max_drawdown = 0.0
    for period_return in returns:
        wealth *= 1.0 + period_return
        peak = max(peak, wealth)
        if peak > 0:
            max_drawdown = min(max_drawdown, wealth / peak - 1.0)

    return {
        "volatility": round(annualized_volatility, 4),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "average_return": round(avg_return, 6),
        "annualized_return": round(annualized_return, 6),
        "max_drawdown": round(max_drawdown, 6),
        "periods_per_year": periods_per_year,
        "observations": len(returns),
    }
