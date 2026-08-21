import { fireEvent, render, screen } from '@testing-library/react';
import App from './App';
import { describe, it, expect } from 'vitest';

describe('App Component', () => {
    it('renders the main title', () => {
        render(<App />);
        expect(screen.getByText(/Quantitative Finance Calculator/i)).toBeInTheDocument();
    });

    it('opens the quantitative calculator tabs', () => {
        render(<App />);
        fireEvent.click(screen.getByRole('button', { name: /option pricing/i }));
        expect(screen.getByRole('heading', { name: /option pricing & greeks/i })).toBeInTheDocument();

        fireEvent.click(screen.getByRole('button', { name: /var & es/i }));
        expect(screen.getByRole('heading', { name: /value at risk & expected shortfall/i })).toBeInTheDocument();
    });
});
