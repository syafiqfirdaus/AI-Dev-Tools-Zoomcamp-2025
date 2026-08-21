import React, { useState } from 'react';
import apiClient from '../api/client';

type PricingModel = 'black_scholes' | 'binomial' | 'monte_carlo';

const OptionPricingCalculator: React.FC = () => {
    const [model, setModel] = useState<PricingModel>('black_scholes');
    const [form, setForm] = useState({
        spot: 100,
        strike: 100,
        time_to_maturity: 1,
        risk_free_rate: 0.05,
        volatility: 0.2,
        dividend_yield: 0,
        option_type: 'call' as 'call' | 'put',
        steps: 200,
        simulations: 50000,
        seed: 42,
        american: false,
    });
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const commonInputs = {
        spot: form.spot,
        strike: form.strike,
        time_to_maturity: form.time_to_maturity,
        risk_free_rate: form.risk_free_rate,
        volatility: form.volatility,
        dividend_yield: form.dividend_yield,
        option_type: form.option_type,
    };

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        try {
            if (model === 'black_scholes') {
                setResult(await apiClient.calculateBlackScholes(commonInputs));
            } else if (model === 'binomial') {
                setResult(await apiClient.calculateBinomialOption({
                    ...commonInputs,
                    steps: form.steps,
                    american: form.american,
                }));
            } else {
                setResult(await apiClient.calculateMonteCarloOption({
                    ...commonInputs,
                    simulations: form.simulations,
                    seed: form.seed,
                }));
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Option pricing failed');
        } finally {
            setLoading(false);
        }
    };

    const numericInput = (name: keyof typeof form, label: string, step = '0.01') => (
        <div className="form-group">
            <label htmlFor={name}>{label}</label>
            <input
                id={name}
                type="number"
                step={step}
                value={form[name] as number}
                onChange={(event) => setForm({ ...form, [name]: parseFloat(event.target.value) })}
                required
            />
        </div>
    );

    return (
        <div className="calculator-container">
            <h2>Option Pricing &amp; Greeks</h2>
            <p className="description">Compare analytical, lattice, and seeded simulation models.</p>
            <form onSubmit={handleSubmit} className="calculator-form">
                <div className="form-group">
                    <label htmlFor="pricing-model">Pricing Model</label>
                    <select id="pricing-model" value={model} onChange={(e) => { setModel(e.target.value as PricingModel); setResult(null); }}>
                        <option value="black_scholes">Black–Scholes &amp; Greeks</option>
                        <option value="binomial">CRR Binomial Tree</option>
                        <option value="monte_carlo">Monte Carlo</option>
                    </select>
                </div>
                <div className="form-group">
                    <label htmlFor="option-type">Option Type</label>
                    <select id="option-type" value={form.option_type} onChange={(e) => setForm({ ...form, option_type: e.target.value as 'call' | 'put' })}>
                        <option value="call">Call</option>
                        <option value="put">Put</option>
                    </select>
                </div>
                {numericInput('spot', 'Spot Price')}
                {numericInput('strike', 'Strike Price')}
                {numericInput('time_to_maturity', 'Time to Maturity (years)')}
                {numericInput('risk_free_rate', 'Risk-free Rate (decimal)', '0.001')}
                {numericInput('volatility', 'Annualized Volatility (decimal)', '0.001')}
                {numericInput('dividend_yield', 'Dividend Yield (decimal)', '0.001')}
                {model === 'binomial' && numericInput('steps', 'Tree Steps', '1')}
                {model === 'binomial' && (
                    <div className="form-group checkbox-group">
                        <label><input type="checkbox" checked={form.american} onChange={(e) => setForm({ ...form, american: e.target.checked })} /> American exercise</label>
                    </div>
                )}
                {model === 'monte_carlo' && numericInput('simulations', 'Simulations', '1000')}
                {model === 'monte_carlo' && numericInput('seed', 'Random Seed', '1')}
                <button className="calculate-btn" disabled={loading}>{loading ? 'Pricing...' : 'Price Option'}</button>
            </form>
            {error && <div className="error-message">{error}</div>}
            {result && (
                <div className="results-container">
                    <h3>{result.model.replace('_', ' ')} result</h3>
                    <div className="results-grid">
                        <div className="result-card"><div className="result-label">Option Price</div><div className="result-value">${result.price.toFixed(4)}</div></div>
                        {result.delta !== undefined && ['delta', 'gamma', 'vega', 'theta', 'rho'].map((greek) => (
                            <div className="result-card" key={greek}><div className="result-label">{greek}</div><div className="result-value">{result[greek].toFixed(4)}</div></div>
                        ))}
                        {result.standard_error !== undefined && <div className="result-card"><div className="result-label">95% Confidence Interval</div><div className="result-value small">${result.confidence_interval_low.toFixed(4)} – ${result.confidence_interval_high.toFixed(4)}</div></div>}
                    </div>
                </div>
            )}
        </div>
    );
};

export default OptionPricingCalculator;
