import React from 'react';
import { render } from '@testing-library/react';
import Loading from './Loading';

it('renders correctly', () => {
  const { queryByTestId } = render(<Loading />);
  expect(queryByTestId('loading-component')).toBeTruthy();
});
