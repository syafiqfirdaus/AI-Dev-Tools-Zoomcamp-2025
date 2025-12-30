import React, { useState } from 'react';
import apiClient from '../api/client';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const InvestmentReturnCalculator: React.FC = () => {
    const [formData, setFormData] = useState({
        initial_value: 10000,
        final_value: 15000,
        years: 5,
    });
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: parseFloat(value)
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const data = await apiClient.calculateInvestmentReturn(formData);
            setResult(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Calculation failed');
        } finally {
            setLoading(false);
        }
    };

    const getChartData = () => {
        if (!result) return [];
        return [
            { name: 'Initial Investment', value: formData.initial_value },
            { name: 'Final Value', value: formData.final_value },
            { name: 'Total Gain', value: result.total_return }
        ];
    };

    return (
        <div className="calculator-container">
            <h2>💰 Investment Return Calculator</h2>
            <p className="description">Calculate ROI and Compound Annual Growth Rate (CAGR)</p>

            <form onSubmit={handleSubmit} className="calculator-form">
                <div className="form-group">
                    <label htmlFor="initial_value">Initial Investment ($)</label>
                    <input
                        type="number"
                        id="initial_value"
                        name="initial_value"
                        value={formData.initial_value}
                        onChange={handleInputChange}
                        min="0"
                        step="100"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="final_value">Final Value ($)</label>
                    <input
                        type="number"
                        id="final_value"
                        name="final_value"
                        value={formData.final_value}
                        onChange={handleInputChange}
                        min="0"
                        step="100"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="years">Time Period (Years)</label>
                    <input
                        type="number"
                        id="years"
                        name="years"
                        value={formData.years}
                        onChange={handleInputChange}
                        min="0.1"
                        step="0.1"
                        required
                    />
                </div>

                <button type="submit" className="calculate-btn" disabled={loading}>
                    {loading ? 'Calculating...' : 'Calculate Returns'}
                </button>
            </form>

            {error && <div className="error-message">{error}</div>}

            {result && (
                <div className="results-container">
                    <h3>Performance Metrics</h3>
                    <div className="results-grid">
                        <div className="result-card">
                            <div className="result-label">ROI (Return on Investment)</div>
                            <div className="result-value green">{(result.roi * 100).toFixed(2)}%</div>
                        </div>
                        <div className="result-card">
                            <div className="result-label">CAGR (Annual Growth)</div>
                            <div className="result-value blue">{(result.cagr * 100).toFixed(2)}%</div>
                            <div className="result-subtitle">Compounded Annual Growth Rate</div>
                        </div>
                        <div className="result-card">
                            <div className="result-label">Total Gain/Loss</div>
                            <div className={`result-value ${result.total_return >= 0 ? 'green' : 'red'}`}>
                                ${result.total_return.toLocaleString()}
                            </div>
                        </div>
                    </div>

                    <div className="chart-container">
                        <h4>Investment Overview</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={getChartData()}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
                                <Bar dataKey="value" name="Amount">
                                    {getChartData().map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={['#8884d8', '#82ca9d', '#ffc658'][index % 3]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    );
};

export default InvestmentReturnCalculator;
