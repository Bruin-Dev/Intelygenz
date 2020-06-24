import React from 'react';
import { render, screen } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import DispatchDetail from '../pages/dispatch/[id]';
import { withTestRouter } from '../components/menu/Menu.test';
import axiosI from '../services/api';
import { API_URLS } from '../services/api.config';
import { mockCtsSingleDispatch } from '../services/mocks/data/cts/single-dispatch.mock';

describe('DISPATCH DETAIL PAGE tests', () => {
  let mockadapter;

  beforeEach(() => {
    mockadapter = new MockAdapter(axiosI);
  });

  afterEach(() => {
    mockadapter.reset();
  });

  const component = withTestRouter(<DispatchDetail />, {
    push: jest.fn(),
    pathname: '/',
    asPath: '/',
    query: { id: 'DIS1234', vendor: 'CTS' }
  });

  it('renders correctly with loading', () => {
    mockadapter
      .onGet(new RegExp(`${API_URLS.DISPATCH_CTS}/*`))
      .reply(200, mockCtsSingleDispatch);
    const { queryByTestId } = render(component);
    expect(queryByTestId('dispatch-detail-loading-page')).toBeTruthy();
  });

  it('renders correctly with not found dispatch data', async () => {
    mockadapter
      .onGet(new RegExp(`${API_URLS.DISPATCH_LIT}/*`))
      .reply(400, { error: 'Error!' });
    render(component);
    expect(
      await screen.findByText(
        'There are problems obtaining the requested information.'
      )
    ).toBeInTheDocument();
  });
});
