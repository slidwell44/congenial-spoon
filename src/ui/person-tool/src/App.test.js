import { render, screen } from '@testing-library/react';
import App from './App';

test('renders dashboard navigation link', () => {
  render(<App />);
  const navLink = screen.getByText(/dashboard/i);
  expect(navLink).toBeInTheDocument();
});
