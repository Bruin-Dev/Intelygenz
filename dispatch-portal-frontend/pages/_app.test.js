import React from 'react';
import { render } from '@testing-library/react';
import { toBeInTheDocument } from '@testing-library/jest-dom';
import MyApp from './_app';

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
