import React from 'react';
import { render } from '@testing-library/react';
import VendorDispatchLink from './VendorDispatchLink';

describe('VendorDispatchLink Button test', () => {
  it('renders correctly', () => {
    const { queryByTestId } = render(
      <VendorDispatchLink dispatchId="XXXXX" vendor="c" />
    );
    expect(queryByTestId('vendorDispatchLink-component')).toBeTruthy();
  });
});
