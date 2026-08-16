import React, { useState } from 'react';
import apiClient from '../api/client';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    AreaChart, Area
} from 'recharts';

const LoanAmortizationCalculator: React.FC = () => {
    const [formData, setFormData] = useState({
        principal: 200000,
        annual_rate: 0.05,
        term_years: 30,
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

    const handleRateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData(prev => ({
            ...prev,
            annual_rate: parseFloat(e.target.value) / 100
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const data = await apiClient.calculateLoanAmortization(formData);
            setResult(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Calculation failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="calculator-container">
            <h2>🏠 Loan Amortization Calculator</h2>
            <p className="description">Calculate monthly payments and view your complete amortization schedule</p>

            <form onSubmit={handleSubmit} className="calculator-form">
                <div className="form-group">
                    <label htmlFor="principal">Loan Amount ($)</label>
                    <input
                        type="number"
                        id="principal"
                        name="principal"
                        value={formData.principal}
                        onChange={handleInputChange}
                        min="1000"
                        step="1000"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="annual_rate">Annual Interest Rate (%)</label>
                    <input
                        type="number"
                        id="annual_rate"
                        name="annual_rate"
                        value={formData.annual_rate * 100}
                        onChange={handleRateChange}
                        min="0.1"
                        max="100"
                        step="0.1"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="term_years">Loan Term (Years)</label>
                    <input
                        type="number"
                        id="term_years"
                        name="term_years"
                        value={formData.term_years}
                        onChange={handleInputChange}
                        min="1"
                        max="50"
                        step="1"
                        required
                    />
                </div>

                <button type="submit" className="calculate-btn" disabled={loading}>
                    {loading ? 'Calculating...' : 'Calculate Payment'}
                </button>
            </form>

            {error && <div className="error-message">{error}</div>}

            {result && (
                <div className="results-container">
                    <h3>Payment Summary</h3>
                    <div className="results-grid">
                        <div className="result-card">
                            <div className="result-label">Monthly Payment</div>
                            <div className="result-value">${result.monthly_payment.toLocaleString(undefined, { maximumFractionDigits: 2 })}</div>
                        </div>
                        <div className="result-card">
                            <div className="result-label">Total Payment</div>
                            <div className="result-value">${result.total_payment.toLocaleString(undefined, { maximumFractionDigits: 2 })}</div>
                        </div>
                        <div className="result-card">
                            <div className="result-label">Total Interest</div>
                            <div className="result-value red">${result.total_interest.toLocaleString(undefined, { maximumFractionDigits: 2 })}</div>
                        </div>
                    </div>

                    <div className="chart-container">
                        <h4>Balance Over Time</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <AreaChart data={result.amortization_schedule.filter((_: any, i: number) => i % 12 === 0)}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="period" label={{ value: 'Months', position: 'insideBottom', offset: -5 }} />
                                <YAxis label={{ value: 'Balance ($)', angle: -90, position: 'insideLeft' }} />
                                <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
                                <Area type="monotone" dataKey="remaining_balance" stroke="#8884d8" fill="#8884d8" name="Remaining Balance" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="chart-container">
                        <h4>Interest vs Principal Paydown (Yearly)</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={result.amortization_schedule.filter((_: any, i: number) => i % 12 === 0)}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="period" />
                                <YAxis />
                                <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
                                <Legend />
                                <Line type="monotone" dataKey="interest_payment" stroke="#ff7300" name="Interest Paid" dot={false} />
                                <Line type="monotone" dataKey="principal_payment" stroke="#82ca9d" name="Principal Paid" dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LoanAmortizationCalculator;
