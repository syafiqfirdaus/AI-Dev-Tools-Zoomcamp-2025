import React, { useState } from 'react';
import apiClient from '../api/client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const CompoundInterestCalculator: React.FC = () => {
    const [formData, setFormData] = useState({
        principal: 10000,
        rate: 0.05,
        time: 10,
        compounds_per_year: 12,
    });
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'compounds_per_year' ? parseInt(value) : parseFloat(value)
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const data = await apiClient.calculateCompoundInterest(formData);
            setResult(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Calculation failed');
        } finally {
            setLoading(false);
        }
    };

    // Generate chart data
    const generateChartData = () => {
        if (!result) return [];
        const data = [];
        const { principal, rate, time, compounds_per_year } = formData;

        for (let t = 0; t <= time; t++) {
            const value = principal * Math.pow(1 + rate / compounds_per_year, compounds_per_year * t);
            data.push({ year: t, value: Math.round(value * 100) / 100 });
        }
        return data;
    };

    return (
        <div className="calculator-container">
            <h2>📈 Compound Interest Calculator</h2>
            <p className="description">Calculate the future value of your investment with compound interest</p>

            <form onSubmit={handleSubmit} className="calculator-form">
                <div className="form-group">
                    <label htmlFor="principal">Principal Amount ($)</label>
                    <input
                        type="number"
                        id="principal"
                        name="principal"
                        value={formData.principal}
                        onChange={handleInputChange}
                        min="0"
                        step="100"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="rate">Annual Interest Rate (%)</label>
                    <input
                        type="number"
                        id="rate"
                        name="rate"
                        value={formData.rate * 100}
                        onChange={(e) => setFormData(prev => ({ ...prev, rate: parseFloat(e.target.value) / 100 }))}
                        min="0"
                        max="100"
                        step="0.1"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="time">Time Period (years)</label>
                    <input
                        type="number"
                        id="time"
                        name="time"
                        value={formData.time}
                        onChange={handleInputChange}
                        min="0"
                        step="1"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="compounds_per_year">Compounding Frequency</label>
                    <select
                        id="compounds_per_year"
                        name="compounds_per_year"
                        value={formData.compounds_per_year}
                        onChange={handleInputChange}
                        required
                    >
                        <option value="1">Annually</option>
                        <option value="2">Semi-Annually</option>
                        <option value="4">Quarterly</option>
                        <option value="12">Monthly</option>
                        <option value="52">Weekly</option>
                        <option value="365">Daily</option>
                    </select>
                </div>

                <button type="submit" className="calculate-btn" disabled={loading}>
                    {loading ? 'Calculating...' : 'Calculate'}
                </button>
            </form>

            {error && <div className="error-message">{error}</div>}

            {result && (
                <div className="results-container">
                    <h3>Results</h3>
                    <div className="results-grid">
                        <div className="result-card">
                            <div className="result-label">Future Value</div>
                            <div className="result-value">${result.future_value.toLocaleString()}</div>
                        </div>
                        <div className="result-card">
                            <div className="result-label">Total Interest</div>
                            <div className="result-value green">${result.total_interest.toLocaleString()}</div>
                        </div>
                    </div>

                    <div className="chart-container">
                        <h4>Growth Over Time</h4>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={generateChartData()}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="year" label={{ value: 'Years', position: 'insideBottom', offset: -5 }} />
                                <YAxis label={{ value: 'Value ($)', angle: -90, position: 'insideLeft' }} />
                                <Tooltip />
                                <Legend />
                                <Line type="monotone" dataKey="value" stroke="#8884d8" strokeWidth={2} name="Investment Value" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CompoundInterestCalculator;
