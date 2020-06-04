import React from 'react';
// eslint-disable-next-line import/no-extraneous-dependencies
import { render, screen } from '@testing-library/react';
import DispatchDetail from './[id]';
import { withTestRouter } from '../../components/menu/Menu.test';

describe('DISPATCH DETAIL PAGE tests', () => {
  const component = withTestRouter(<DispatchDetail />, {
    push: jest.fn(),
    pathname: '/',
    asPath: '/',
    query: 'DIS1234'
  });

  it('renders correctly with loading', () => {
    const { queryByTestId } = render(component);
    expect(queryByTestId('dispatch-detail-loading-page')).toBeTruthy();
  });

  it('renders correctly with not found dispatch data', async () => {
    render(component);
    expect(await screen.findByText('Not found dispatch')).toBeInTheDocument();
  });
});
