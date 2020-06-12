import React from 'react';
import { render } from '@testing-library/react';
import MyApp from '../pages/_app';

describe('MYAPP(_APP) tests', () => {
  const MockApp = () => <p>Hello from your Mock App</p>;

  it('renders correctly', () => {
    const { getByText } = render(
      MyApp({
        Component: MockApp,
        pageProps: {}
      })
    );
    expect(getByText(/Hello from your Mock App/i)).toBeInTheDocument();
  });
});
