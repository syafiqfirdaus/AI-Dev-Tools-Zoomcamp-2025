/**
 * Centralized API client for backend communication
 */
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
    private client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: API_BASE_URL,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            (error) => {
                console.error('API Error:', error.response?.data || error.message);
                return Promise.reject(error);
            }
        );
    }

    // Compound Interest
    async calculateCompoundInterest(data: {
        principal: number;
        rate: number;
        time: number;
        compounds_per_year: number;
    }) {
        const response = await this.client.post('/api/v1/calculate/compound-interest', data);
        return response.data;
    }

    // Loan Amortization
    async calculateLoanAmortization(data: {
        principal: number;
        annual_rate: number;
        term_years: number;
    }) {
        const response = await this.client.post('/api/v1/calculate/loan-amortization', data);
        return response.data;
    }

    // Investment Return
    async calculateInvestmentReturn(data: {
        initial_value: number;
        final_value: number;
        years: number;
    }) {
        const response = await this.client.post('/api/v1/calculate/investment-return', data);
        return response.data;
    }

    // Risk Metrics
    async calculateRiskMetrics(data: {
        returns: number[];
        risk_free_rate: number;
    }) {
        const response = await this.client.post('/api/v1/calculate/risk-metrics', data);
        return response.data;
    }

    // Get History
    async getHistory(params?: {
        limit?: number;
        offset?: number;
        calculation_type?: string;
    }) {
        const response = await this.client.get('/api/v1/history', { params });
        return response.data;
    }
}

export const apiClient = new APIClient();
export default apiClient;
