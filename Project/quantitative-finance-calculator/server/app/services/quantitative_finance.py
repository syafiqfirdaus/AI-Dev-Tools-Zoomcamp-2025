"""Quantitative-finance models with deterministic, dependency-free implementations."""

import math
import random
import statistics
from typing import Literal

OptionType = Literal["call", "put"]
VarMethod = Literal["historical", "parametric"]


def _validate_option_inputs(
    spot: float,
    strike: float,
    time_to_maturity: float,
    volatility: float,
    option_type: OptionType,
) -> None:
    if spot <= 0:
        raise ValueError("Spot price must be positive")
    if strike <= 0:
        raise ValueError("Strike price must be positive")
    if time_to_maturity <= 0:
        raise ValueError("Time to maturity must be positive")
    if volatility <= 0:
        raise ValueError("Volatility must be positive")
    if option_type not in ("call", "put"):
        raise ValueError("Option type must be 'call' or 'put'")


def _normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def _normal_pdf(value: float) -> float:
    return math.exp(-0.5 * value * value) / math.sqrt(2.0 * math.pi)


def calculate_black_scholes(
    spot: float,
    strike: float,
    time_to_maturity: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType,
    dividend_yield: float = 0.0,
) -> dict[str, float | str]:
    """Price a European option and return its analytical Greeks.

    Vega and rho are reported for a 1.00 absolute change in volatility and rate;
    theta is the value change per year.
    """
    _validate_option_inputs(spot, strike, time_to_maturity, volatility, option_type)

    sqrt_time = math.sqrt(time_to_maturity)
    discount_rate = math.exp(-risk_free_rate * time_to_maturity)
    discount_dividend = math.exp(-dividend_yield * time_to_maturity)
    d1 = (
        math.log(spot / strike)
        + (risk_free_rate - dividend_yield + 0.5 * volatility**2) * time_to_maturity
    ) / (volatility * sqrt_time)
    d2 = d1 - volatility * sqrt_time

    common_theta = -spot * discount_dividend * _normal_pdf(d1) * volatility / (2.0 * sqrt_time)
    if option_type == "call":
        price = spot * discount_dividend * _normal_cdf(d1) - strike * discount_rate * _normal_cdf(
            d2
        )
        delta = discount_dividend * _normal_cdf(d1)
        theta = (
            common_theta
            - risk_free_rate * strike * discount_rate * _normal_cdf(d2)
            + dividend_yield * spot * discount_dividend * _normal_cdf(d1)
        )
        rho = strike * time_to_maturity * discount_rate * _normal_cdf(d2)
    else:
        price = strike * discount_rate * _normal_cdf(-d2) - spot * discount_dividend * _normal_cdf(
            -d1
        )
        delta = discount_dividend * (_normal_cdf(d1) - 1.0)
        theta = (
            common_theta
            + risk_free_rate * strike * discount_rate * _normal_cdf(-d2)
            - dividend_yield * spot * discount_dividend * _normal_cdf(-d1)
        )
        rho = -strike * time_to_maturity * discount_rate * _normal_cdf(-d2)

    gamma = discount_dividend * _normal_pdf(d1) / (spot * volatility * sqrt_time)
    vega = spot * discount_dividend * _normal_pdf(d1) * sqrt_time

    return {
        "model": "black_scholes",
        "option_type": option_type,
        "price": round(price, 6),
        "delta": round(delta, 6),
        "gamma": round(gamma, 6),
        "vega": round(vega, 6),
        "theta": round(theta, 6),
        "rho": round(rho, 6),
    }


def calculate_binomial_option(
    spot: float,
    strike: float,
    time_to_maturity: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType,
    steps: int = 200,
    dividend_yield: float = 0.0,
    american: bool = False,
) -> dict[str, float | int | str | bool]:
    """Price a European or American option using a Cox-Ross-Rubinstein tree."""
    _validate_option_inputs(spot, strike, time_to_maturity, volatility, option_type)
    if steps < 1:
        raise ValueError("Steps must be at least 1")

    dt = time_to_maturity / steps
    up = math.exp(volatility * math.sqrt(dt))
    down = 1.0 / up
    probability = (math.exp((risk_free_rate - dividend_yield) * dt) - down) / (up - down)
    if not 0.0 <= probability <= 1.0:
        raise ValueError("Inputs violate the binomial tree no-arbitrage condition")

    discount = math.exp(-risk_free_rate * dt)

    def payoff(asset_price: float) -> float:
        if option_type == "call":
            return max(asset_price - strike, 0.0)
        return max(strike - asset_price, 0.0)

    values = [payoff(spot * up**j * down ** (steps - j)) for j in range(steps + 1)]
    for level in range(steps - 1, -1, -1):
        for node in range(level + 1):
            continuation = discount * (
                probability * values[node + 1] + (1.0 - probability) * values[node]
            )
            if american:
                asset_price = spot * up**node * down ** (level - node)
                values[node] = max(continuation, payoff(asset_price))
            else:
                values[node] = continuation

    return {
        "model": "binomial",
        "option_type": option_type,
        "price": round(values[0], 6),
        "steps": steps,
        "american": american,
    }


def calculate_monte_carlo_option(
    spot: float,
    strike: float,
    time_to_maturity: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType,
    simulations: int = 50_000,
    dividend_yield: float = 0.0,
    seed: int = 42,
) -> dict[str, float | int | str]:
    """Price a European option with seeded antithetic Monte Carlo simulation."""
    _validate_option_inputs(spot, strike, time_to_maturity, volatility, option_type)
    if simulations < 1_000:
        raise ValueError("Simulations must be at least 1000")
    if simulations % 2 != 0:
        raise ValueError("Simulations must be even when using antithetic variates")

    rng = random.Random(seed)
    drift = (risk_free_rate - dividend_yield - 0.5 * volatility**2) * time_to_maturity
    diffusion = volatility * math.sqrt(time_to_maturity)
    paired_payoffs: list[float] = []

    def payoff(asset_price: float) -> float:
        if option_type == "call":
            return max(asset_price - strike, 0.0)
        return max(strike - asset_price, 0.0)

    for _ in range(simulations // 2):
        normal_draw = rng.gauss(0.0, 1.0)
        positive_payoff = payoff(spot * math.exp(drift + diffusion * normal_draw))
        negative_payoff = payoff(spot * math.exp(drift - diffusion * normal_draw))
        paired_payoffs.append((positive_payoff + negative_payoff) / 2.0)

    discount = math.exp(-risk_free_rate * time_to_maturity)
    price = discount * statistics.fmean(paired_payoffs)
    standard_error = discount * statistics.stdev(paired_payoffs) / math.sqrt(len(paired_payoffs))
    confidence_width = 1.96 * standard_error

    return {
        "model": "monte_carlo",
        "option_type": option_type,
        "price": round(price, 6),
        "standard_error": round(standard_error, 6),
        "confidence_interval_low": round(price - confidence_width, 6),
        "confidence_interval_high": round(price + confidence_width, 6),
        "simulations": simulations,
        "seed": seed,
    }


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def calculate_value_at_risk(
    returns: list[float],
    portfolio_value: float,
    confidence_level: float = 0.95,
    method: VarMethod = "historical",
) -> dict[str, float | int | str]:
    """Calculate one-period VaR and Expected Shortfall as positive loss amounts."""
    if len(returns) < 2:
        raise ValueError("At least 2 return values required")
    if portfolio_value <= 0:
        raise ValueError("Portfolio value must be positive")
    if not 0.5 < confidence_level < 1.0:
        raise ValueError("Confidence level must be between 0.5 and 1")
    if method not in ("historical", "parametric"):
        raise ValueError("Method must be 'historical' or 'parametric'")

    tail_probability = 1.0 - confidence_level
    if method == "historical":
        cutoff_return = _quantile(returns, tail_probability)
        tail_returns = [value for value in returns if value <= cutoff_return]
        expected_shortfall_return = statistics.fmean(tail_returns)
    else:
        mean_return = statistics.fmean(returns)
        volatility = statistics.stdev(returns)
        z_score = statistics.NormalDist().inv_cdf(tail_probability)
        cutoff_return = mean_return + z_score * volatility
        expected_shortfall_return = mean_return - (
            volatility * _normal_pdf(z_score) / tail_probability
        )

    return {
        "method": method,
        "confidence_level": confidence_level,
        "value_at_risk": round(max(0.0, -cutoff_return * portfolio_value), 2),
        "expected_shortfall": round(max(0.0, -expected_shortfall_return * portfolio_value), 2),
        "observations": len(returns),
    }
