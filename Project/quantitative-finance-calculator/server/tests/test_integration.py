"""
Integration tests for API endpoints with database
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create and drop database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestCompoundInterestAPI:
    def test_valid_request(self):
        """Test valid compound interest request"""
        response = client.post(
            "/api/v1/calculate/compound-interest",
            json={"principal": 10000, "rate": 0.05, "time": 10, "compounds_per_year": 12},
        )
        assert response.status_code == 200
        data = response.json()
        assert "future_value" in data
        assert "total_interest" in data
        assert "calculation_id" in data
        assert data["future_value"] == pytest.approx(16470.09, rel=1e-2)

    def test_invalid_rate(self):
        """Test with invalid interest rate"""
        response = client.post(
            "/api/v1/calculate/compound-interest",
            json={
                "principal": 10000,
                "rate": 1.5,  # Invalid: > 1
                "time": 10,
                "compounds_per_year": 12,
            },
        )
        assert response.status_code == 422  # Validation error


class TestLoanAmortizationAPI:
    def test_valid_request(self):
        """Test valid loan amortization request"""
        response = client.post(
            "/api/v1/calculate/loan-amortization",
            json={"principal": 300000, "annual_rate": 0.045, "term_years": 30},
        )
        assert response.status_code == 200
        data = response.json()
        assert "monthly_payment" in data
        assert "amortization_schedule" in data
        assert len(data["amortization_schedule"]) == 360


class TestInvestmentReturnAPI:
    def test_valid_request(self):
        """Test valid investment return request"""
        response = client.post(
            "/api/v1/calculate/investment-return",
            json={"initial_value": 10000, "final_value": 15000, "years": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert "roi" in data
        assert "cagr" in data
        assert data["roi"] == pytest.approx(50.0, rel=1e-2)


class TestRiskMetricsAPI:
    def test_valid_request(self):
        """Test valid risk metrics request"""
        response = client.post(
            "/api/v1/calculate/risk-metrics",
            json={"returns": [0.05, 0.03, -0.02, 0.08, 0.04], "risk_free_rate": 0.02},
        )
        assert response.status_code == 200
        data = response.json()
        assert "volatility" in data
        assert "sharpe_ratio" in data
        assert "average_return" in data

    def test_negative_rate_and_monthly_frequency(self):
        response = client.post(
            "/api/v1/calculate/risk-metrics",
            json={
                "returns": [0.01, 0.02, -0.01, 0.015],
                "risk_free_rate": -0.005,
                "periods_per_year": 12,
            },
        )
        assert response.status_code == 200
        assert response.json()["periods_per_year"] == 12


class TestQuantitativeFinanceAPI:
    def test_black_scholes_endpoint(self):
        response = client.post(
            "/api/v1/calculate/option-pricing/black-scholes",
            json={
                "spot": 100,
                "strike": 100,
                "time_to_maturity": 1,
                "risk_free_rate": 0.05,
                "volatility": 0.2,
                "option_type": "call",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == pytest.approx(10.450584, abs=1e-6)
        assert "delta" in data
        assert "calculation_id" in data

    def test_binomial_and_monte_carlo_endpoints(self):
        base_request = {
            "spot": 100,
            "strike": 100,
            "time_to_maturity": 1,
            "risk_free_rate": 0.05,
            "volatility": 0.2,
            "option_type": "put",
        }
        tree = client.post(
            "/api/v1/calculate/option-pricing/binomial",
            json={**base_request, "steps": 100, "american": True},
        )
        simulation = client.post(
            "/api/v1/calculate/option-pricing/monte-carlo",
            json={**base_request, "simulations": 2_000, "seed": 42},
        )
        assert tree.status_code == 200
        assert tree.json()["american"] is True
        assert simulation.status_code == 200
        assert simulation.json()["confidence_interval_low"] < simulation.json()["price"]

    def test_value_at_risk_endpoint(self):
        response = client.post(
            "/api/v1/calculate/value-at-risk",
            json={
                "returns": [-0.10, -0.05, 0.0, 0.02, 0.03],
                "portfolio_value": 10_000,
                "confidence_level": 0.80,
                "method": "historical",
            },
        )
        assert response.status_code == 200
        assert response.json()["expected_shortfall"] == 1_000


class TestHistoryAPI:
    def test_empty_history(self):
        """Test history with no calculations"""
        response = client.get("/api/v1/history")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_history_after_calculation(self):
        """Test history after performing calculation"""
        # Create a calculation
        client.post(
            "/api/v1/calculate/compound-interest",
            json={"principal": 1000, "rate": 0.05, "time": 5, "compounds_per_year": 12},
        )

        # Get history
        response = client.get("/api/v1/history")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["calculation_type"] == "compound_interest"

    def test_history_pagination(self):
        """Test history pagination"""
        # Create multiple calculations
        for i in range(5):
            client.post(
                "/api/v1/calculate/compound-interest",
                json={
                    "principal": 1000 + i * 100,
                    "rate": 0.05,
                    "time": 5,
                    "compounds_per_year": 12,
                },
            )

        # Get first page
        response = client.get("/api/v1/history?limit=2&offset=0")
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2

        # Get second page
        response = client.get("/api/v1/history?limit=2&offset=2")
        data = response.json()
        assert len(data["items"]) == 2

    def test_history_filter_by_type(self):
        """Test filtering history by calculation type"""
        # Create different types of calculations
        client.post(
            "/api/v1/calculate/compound-interest",
            json={"principal": 1000, "rate": 0.05, "time": 5, "compounds_per_year": 12},
        )
        client.post(
            "/api/v1/calculate/investment-return",
            json={"initial_value": 10000, "final_value": 15000, "years": 5},
        )

        # Filter by type
        response = client.get("/api/v1/history?calculation_type=compound_interest")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["calculation_type"] == "compound_interest"


class TestHealthEndpoints:
    def test_root(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_health(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
