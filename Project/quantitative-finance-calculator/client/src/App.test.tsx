import { render, screen } from '@testing-library/react';
import App from './App';
import { describe, it, expect } from 'vitest';

describe('App Component', () => {
    it('renders the main title', () => {
        render(<App />);
        expect(screen.getByText(/Quantitative Finance Calculator/i)).toBeInTheDocument();
    });
});
