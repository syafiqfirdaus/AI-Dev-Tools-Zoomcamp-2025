"""
Unit tests for financial calculation functions
"""
import pytest
from app.services.finance_calculator import (
    calculate_compound_interest,
    calculate_loan_amortization,
    calculate_investment_return,
    calculate_risk_metrics
)


class TestCompoundInterest:
    def test_basic_calculation(self):
        """Test basic compound interest calculation"""
        result = calculate_compound_interest(
            principal=10000,
            rate=0.05,
            time=10,
            compounds_per_year=12
        )
        assert result["future_value"] == pytest.approx(16470.09, rel=1e-2)
        assert result["total_interest"] == pytest.approx(6470.09, rel=1e-2)
    
    def test_annual_compounding(self):
        """Test with annual compounding"""
        result = calculate_compound_interest(
            principal=1000,
            rate=0.10,
            time=5,
            compounds_per_year=1
        )
        assert result["future_value"] == pytest.approx(1610.51, rel=1e-2)
    
    def test_zero_rate(self):
        """Test with zero interest rate"""
        result = calculate_compound_interest(
            principal=1000,
            rate=0.0,
            time=10,
            compounds_per_year=12
        )
        assert result["future_value"] == 1000.0
        assert result["total_interest"] == 0.0
    
    def test_invalid_principal(self):
        """Test with negative principal"""
        with pytest.raises(ValueError, match="Principal must be non-negative"):
            calculate_compound_interest(-1000, 0.05, 10, 12)
    
    def test_invalid_compounds(self):
        """Test with invalid compounds per year"""
        with pytest.raises(ValueError, match="Compounds per year must be at least 1"):
            calculate_compound_interest(1000, 0.05, 10, 0)


class TestLoanAmortization:
    def test_basic_loan(self):
        """Test basic loan amortization"""
        result = calculate_loan_amortization(
            principal=300000,
            annual_rate=0.045,
            term_years=30
        )
        assert result["monthly_payment"] == pytest.approx(1520.06, rel=1e-2)
        assert len(result["amortization_schedule"]) == 360
        assert result["amortization_schedule"][-1]["balance"] == pytest.approx(0, abs=1)
    
    def test_short_term_loan(self):
        """Test short-term loan"""
        result = calculate_loan_amortization(
            principal=10000,
            annual_rate=0.06,
            term_years=2
        )
        assert result["monthly_payment"] == pytest.approx(443.21, rel=1e-2)
        assert len(result["amortization_schedule"]) == 24
    
    def test_zero_interest_loan(self):
        """Test zero-interest loan"""
        result = calculate_loan_amortization(
            principal=12000,
            annual_rate=0.0,
            term_years=1
        )
        assert result["monthly_payment"] == 1000.0
        assert result["total_interest"] == 0.0
    
    def test_invalid_principal(self):
        """Test with zero or negative principal"""
        with pytest.raises(ValueError, match="Principal must be positive"):
            calculate_loan_amortization(0, 0.05, 10)


class TestInvestmentReturn:
    def test_positive_return(self):
        """Test positive investment return"""
        result = calculate_investment_return(
            initial_value=10000,
            final_value=15000,
            years=5
        )
        assert result["roi"] == pytest.approx(50.0, rel=1e-2)
        assert result["cagr"] == pytest.approx(8.45, rel=1e-1)
        assert result["total_return"] == 5000.0
    
    def test_negative_return(self):
        """Test negative investment return"""
        result = calculate_investment_return(
            initial_value=10000,
            final_value=8000,
            years=3
        )
        assert result["roi"] == pytest.approx(-20.0, rel=1e-2)
        assert result["total_return"] == -2000.0
    
    def test_no_change(self):
        """Test when value doesn't change"""
        result = calculate_investment_return(
            initial_value=10000,
            final_value=10000,
            years=5
        )
        assert result["roi"] == 0.0
        assert result["cagr"] == 0.0
    
    def test_invalid_initial_value(self):
        """Test with invalid initial value"""
        with pytest.raises(ValueError, match="Initial value must be positive"):
            calculate_investment_return(0, 10000, 5)


class TestRiskMetrics:
    def test_basic_risk_metrics(self):
        """Test basic risk metrics calculation"""
        returns = [0.05, 0.03, -0.02, 0.08, 0.04, 0.06, -0.01, 0.07, 0.02, 0.05]
        result = calculate_risk_metrics(
            returns=returns,
            risk_free_rate=0.02
        )
        assert "volatility" in result
        assert "sharpe_ratio" in result
        assert "average_return" in result
        assert result["volatility"] > 0
    
    def test_zero_volatility(self):
        """Test with constant returns (zero volatility)"""
        returns = [0.05, 0.05, 0.05, 0.05]
        result = calculate_risk_metrics(
            returns=returns,
            risk_free_rate=0.02
        )
        assert result["volatility"] == 0.0
        assert result["sharpe_ratio"] == 0.0
    
    def test_insufficient_data(self):
        """Test with insufficient return data"""
        with pytest.raises(ValueError, match="At least 2 return values required"):
            calculate_risk_metrics([0.05], 0.02)
    
    def test_negative_risk_free_rate(self):
        """Test with negative risk-free rate"""
        with pytest.raises(ValueError, match="Risk-free rate must be non-negative"):
            calculate_risk_metrics([0.05, 0.03, 0.04], -0.01)
