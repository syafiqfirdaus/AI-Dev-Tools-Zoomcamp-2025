"""Reference and cross-model tests for the quantitative-finance models."""

import math

import pytest

from app.services.quantitative_finance import (
    calculate_binomial_option,
    calculate_black_scholes,
    calculate_monte_carlo_option,
    calculate_value_at_risk,
)

OPTION_INPUTS = {
    "spot": 100.0,
    "strike": 100.0,
    "time_to_maturity": 1.0,
    "risk_free_rate": 0.05,
    "volatility": 0.2,
}


class TestBlackScholes:
    def test_textbook_at_the_money_benchmark(self):
        """Validate against the standard S=K=100, r=5%, sigma=20%, T=1 benchmark."""
        call = calculate_black_scholes(**OPTION_INPUTS, option_type="call")
        put = calculate_black_scholes(**OPTION_INPUTS, option_type="put")

        assert call["price"] == pytest.approx(10.450584, abs=1e-6)
        assert put["price"] == pytest.approx(5.573526, abs=1e-6)
        assert call["delta"] == pytest.approx(0.636831, abs=1e-6)
        assert call["gamma"] == pytest.approx(0.018762, abs=1e-6)
        assert call["vega"] == pytest.approx(37.524035, abs=1e-6)

    def test_put_call_parity_with_negative_rate(self):
        inputs = {**OPTION_INPUTS, "risk_free_rate": -0.005}
        call = calculate_black_scholes(**inputs, option_type="call")
        put = calculate_black_scholes(**inputs, option_type="put")
        parity = inputs["spot"] - inputs["strike"] * math.exp(
            -inputs["risk_free_rate"] * inputs["time_to_maturity"]
        )
        assert call["price"] - put["price"] == pytest.approx(parity, abs=2e-6)


class TestNumericalOptionModels:
    def test_binomial_tree_converges_to_black_scholes(self):
        analytical = calculate_black_scholes(**OPTION_INPUTS, option_type="call")
        tree = calculate_binomial_option(**OPTION_INPUTS, option_type="call", steps=500)
        assert tree["price"] == pytest.approx(analytical["price"], abs=0.01)

    def test_american_put_is_not_worth_less_than_european_put(self):
        european = calculate_binomial_option(
            **OPTION_INPUTS, option_type="put", steps=300, american=False
        )
        american = calculate_binomial_option(
            **OPTION_INPUTS, option_type="put", steps=300, american=True
        )
        assert american["price"] >= european["price"]

    def test_seeded_monte_carlo_interval_contains_analytical_price(self):
        analytical = calculate_black_scholes(**OPTION_INPUTS, option_type="call")
        simulation = calculate_monte_carlo_option(
            **OPTION_INPUTS,
            option_type="call",
            simulations=50_000,
            seed=7,
        )
        assert simulation["confidence_interval_low"] <= analytical["price"]
        assert analytical["price"] <= simulation["confidence_interval_high"]
        repeated = calculate_monte_carlo_option(
            **OPTION_INPUTS,
            option_type="call",
            simulations=50_000,
            seed=7,
        )
        assert repeated == simulation

    def test_antithetic_simulation_requires_pairs(self):
        with pytest.raises(ValueError, match="must be even"):
            calculate_monte_carlo_option(
                **OPTION_INPUTS,
                option_type="call",
                simulations=1_001,
            )


class TestValueAtRisk:
    def test_historical_var_and_expected_shortfall_known_sample(self):
        result = calculate_value_at_risk(
            returns=[-0.10, -0.05, 0.0, 0.02, 0.03],
            portfolio_value=10_000,
            confidence_level=0.80,
            method="historical",
        )
        assert result["value_at_risk"] == pytest.approx(600.0)
        assert result["expected_shortfall"] == pytest.approx(1_000.0)

    def test_parametric_expected_shortfall_exceeds_var(self):
        result = calculate_value_at_risk(
            returns=[-0.04, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03],
            portfolio_value=100_000,
            confidence_level=0.95,
            method="parametric",
        )
        assert result["expected_shortfall"] > result["value_at_risk"] > 0

    @pytest.mark.parametrize("method", ["historical", "parametric"])
    def test_rejects_invalid_confidence(self, method):
        with pytest.raises(ValueError, match="Confidence level"):
            calculate_value_at_risk([0.01, -0.01], 10_000, 1.0, method)
