import { useState } from 'react';
import CompoundInterestCalculator from './components/CompoundInterestCalculator';
import LoanAmortizationCalculator from './components/LoanAmortizationCalculator';
import InvestmentReturnCalculator from './components/InvestmentReturnCalculator';
import RiskMetricsCalculator from './components/RiskMetricsCalculator';
import OptionPricingCalculator from './components/OptionPricingCalculator';
import ValueAtRiskCalculator from './components/ValueAtRiskCalculator';
import './App.css';

function App() {
    const [activeTab, setActiveTab] = useState('compound');

    return (
        <div className="app">
            <header className="app-header">
                <h1>🧮 Quantitative Finance Calculator</h1>
                <p>Professional financial calculations made simple</p>
            </header>

            <nav className="tab-navigation">
                <button
                    className={activeTab === 'compound' ? 'tab-active' : ''}
                    onClick={() => setActiveTab('compound')}
                >
                    Compound Interest
                </button>
                <button
                    className={activeTab === 'loan' ? 'tab-active' : ''}
                    onClick={() => setActiveTab('loan')}
                >
                    Loan Amortization
                </button>
                <button
                    className={activeTab === 'investment' ? 'tab-active' : ''}
                    onClick={() => setActiveTab('investment')}
                >
                    Investment Return
                </button>
                <button
                    className={activeTab === 'options' ? 'tab-active' : ''}
                    onClick={() => setActiveTab('options')}
                >
                    Option Pricing
                </button>
                <button
                    className={activeTab === 'var' ? 'tab-active' : ''}
                    onClick={() => setActiveTab('var')}
                >
                    VaR &amp; ES
                </button>
                <button
                    className={activeTab === 'risk' ? 'tab-active' : ''}
                    onClick={() => setActiveTab('risk')}
                >
                    Risk Metrics
                </button>
            </nav>

            <main className="main-content">
                {activeTab === 'compound' && <CompoundInterestCalculator />}
                {activeTab === 'loan' && <LoanAmortizationCalculator />}
                {activeTab === 'investment' && <InvestmentReturnCalculator />}
                {activeTab === 'options' && <OptionPricingCalculator />}
                {activeTab === 'var' && <ValueAtRiskCalculator />}
                {activeTab === 'risk' && <RiskMetricsCalculator />}
            </main>

            <footer className="app-footer">
                <p>Built with ❤️ using AI-assisted development</p>
                <p>AI Dev Tools Zoomcamp 2025 | Google Antigravity × Claude Sonnet 4.5</p>
            </footer>
        </div>
    );
}

export default App;
