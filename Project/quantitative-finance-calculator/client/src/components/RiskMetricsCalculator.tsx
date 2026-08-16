import React, { useState } from 'react';
import apiClient from '../api/client';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';

const RiskMetricsCalculator: React.FC = () => {
    const [rawReturns, setRawReturns] = useState("0.05, 0.02, -0.01, 0.04, 0.03, -0.02, 0.06, 0.01, 0.03, 0.04");
    const [riskFreeRate, setRiskFreeRate] = useState(0.02);
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Parse comma-separated string to number array
            const returnsArray = rawReturns.split(',').map(v => parseFloat(v.trim())).filter(n => !isNaN(n));

            if (returnsArray.length < 2) {
                throw new Error("Please provide at least 2 return values");
            }

            const data = await apiClient.calculateRiskMetrics({
                returns: returnsArray,
                risk_free_rate: riskFreeRate
            });
            setResult(data);
        } catch (err: any) {
            setError(err.message || err.response?.data?.detail || 'Calculation failed');
        } finally {
            setLoading(false);
        }
    };

    const getChartData = () => {
        if (!result) return [];
        const returnsArray = rawReturns.split(',').map(v => parseFloat(v.trim())).filter(n => !isNaN(n));
        return returnsArray.map((val, idx) => ({ period: idx + 1, return: val }));
    };

    return (
        <div className="calculator-container">
            <h2>⚠️ Risk Metrics Calculator</h2>
            <p className="description">Analyze volatility and risk-adjusted returns (Sharpe Ratio)</p>

            <form onSubmit={handleSubmit} className="calculator-form">
                <div className="form-group full-width">
                    <label htmlFor="returns">Historical Returns (comma separated decimals, e.g. 0.05 for 5%)</label>
                    <textarea
                        id="returns"
                        rows={4}
                        value={rawReturns}
                        onChange={(e) => setRawReturns(e.target.value)}
                        placeholder="0.05, 0.02, -0.01, ..."
                        className="text-input"
                        required
                    />
                    <small>Enter a series of periodic returns (e.g. monthly or yearly)</small>
                </div>

                <div className="form-group">
                    <label htmlFor="risk_free_rate">Risk Free Rate (decimal)</label>
                    <input
                        type="number"
                        id="risk_free_rate"
                        value={riskFreeRate}
                        onChange={(e) => setRiskFreeRate(parseFloat(e.target.value))}
                        step="0.001"
                        required
                    />
                </div>

                <button type="submit" className="calculate-btn" disabled={loading}>
                    {loading ? 'Calculating...' : 'Calculate Risk Metrics'}
                </button>
            </form>

            {error && <div className="error-message">{error}</div>}

            {result && (
                <div className="results-container">
                    <h3>Risk Analysis</h3>
                    <div className="results-grid">
                        <div className="result-card">
                            <div className="result-label">Annualized Volatility</div>
                            <div className="result-value blue">{(result.volatility * 100).toFixed(2)}%</div>
                            <div className="result-subtitle">Standard Deviation</div>
                        </div>
                        <div className="result-card">
                            <div className="result-label">Sharpe Ratio</div>
                            <div className={`result-value ${result.sharpe_ratio > 1 ? 'green' : 'orange'}`}>
                                {result.sharpe_ratio.toFixed(4)}
                            </div>
                            <div className="result-subtitle">Risk-Adjusted Return</div>
                        </div>
                        <div className="result-card">
                            <div className="result-label">Max Drawdown</div>
                            <div className="result-value red">{(result.max_drawdown * 100).toFixed(2)}%</div>
                        </div>
                    </div>

                    <div className="chart-container">
                        <h4>Returns Distribution</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={getChartData()}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="period" label={{ value: 'Period', position: 'insideBottom', offset: -5 }} />
                                <YAxis label={{ value: 'Return', angle: -90, position: 'insideLeft' }} />
                                <Tooltip />
                                <ReferenceLine y={0} stroke="#666" />
                                <Line type="monotone" dataKey="return" stroke="#8884d8" strokeWidth={2} dot={{ r: 4 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RiskMetricsCalculator;
