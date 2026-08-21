import React, { useState } from 'react';
import apiClient from '../api/client';

const ValueAtRiskCalculator: React.FC = () => {
    const [rawReturns, setRawReturns] = useState('-0.025, 0.012, -0.008, 0.018, -0.035, 0.006, 0.021, -0.011, 0.009, -0.016');
    const [portfolioValue, setPortfolioValue] = useState(100000);
    const [confidenceLevel, setConfidenceLevel] = useState(0.95);
    const [method, setMethod] = useState<'historical' | 'parametric'>('historical');
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        const returns = rawReturns.split(',').map((value) => Number(value.trim())).filter(Number.isFinite);
        setLoading(true);
        setError(null);
        try {
            setResult(await apiClient.calculateValueAtRisk({
                returns,
                portfolio_value: portfolioValue,
                confidence_level: confidenceLevel,
                method,
            }));
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Risk calculation failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="calculator-container">
            <h2>Value at Risk &amp; Expected Shortfall</h2>
            <p className="description">Estimate one-period tail losses using historical or normal-parametric returns.</p>
            <form onSubmit={handleSubmit} className="calculator-form">
                <div className="form-group full-width">
                    <label htmlFor="var-returns">Periodic Returns (comma separated decimals)</label>
                    <textarea id="var-returns" rows={5} value={rawReturns} onChange={(e) => setRawReturns(e.target.value)} required />
                </div>
                <div className="form-group">
                    <label htmlFor="portfolio-value">Portfolio Value</label>
                    <input id="portfolio-value" type="number" min="0.01" step="100" value={portfolioValue} onChange={(e) => setPortfolioValue(Number(e.target.value))} required />
                </div>
                <div className="form-group">
                    <label htmlFor="confidence">Confidence Level</label>
                    <select id="confidence" value={confidenceLevel} onChange={(e) => setConfidenceLevel(Number(e.target.value))}>
                        <option value="0.90">90%</option><option value="0.95">95%</option><option value="0.99">99%</option>
                    </select>
                </div>
                <div className="form-group">
                    <label htmlFor="var-method">Method</label>
                    <select id="var-method" value={method} onChange={(e) => setMethod(e.target.value as 'historical' | 'parametric')}>
                        <option value="historical">Historical</option><option value="parametric">Parametric Normal</option>
                    </select>
                </div>
                <button className="calculate-btn" disabled={loading}>{loading ? 'Calculating...' : 'Calculate Tail Risk'}</button>
            </form>
            {error && <div className="error-message">{error}</div>}
            {result && (
                <div className="results-container">
                    <div className="results-grid">
                        <div className="result-card"><div className="result-label">Value at Risk</div><div className="result-value red">${result.value_at_risk.toLocaleString()}</div></div>
                        <div className="result-card"><div className="result-label">Expected Shortfall</div><div className="result-value red">${result.expected_shortfall.toLocaleString()}</div></div>
                        <div className="result-card"><div className="result-label">Sample</div><div className="result-value">{result.observations}</div></div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ValueAtRiskCalculator;
