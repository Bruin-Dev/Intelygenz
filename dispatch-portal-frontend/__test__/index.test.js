import React from 'react';
import { render, screen, act } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import Index from '../pages/index';
import { dispatchList } from '../services/mocks/list-dispatch.mock';
import { API_URLS } from '../services/api.config';
import axiosI from '../services/api';

describe('DASHBOARD PAGE tests', () => {
  let mockadapter;

  beforeEach(() => {
    mockadapter = new MockAdapter(axiosI);
  });

  afterEach(() => {
    mockadapter.reset();
  });

  it('renders correctly', () => {
    const { queryByTestId } = render(<Index />);
    expect(queryByTestId('index-page-component')).toBeTruthy();
  });

  it('renders correctly with loading', () => {
    const { getByText } = render(<Index />);
    expect(getByText('Loading...')).toBeTruthy();
  });

  it('renders correctly with list of dispatch', async () => {
    mockadapter.onGet(API_URLS.DISPATCH).reply(200, {
      vendor: 'lit',
      list_dispatch: dispatchList.data
    });

    act(() => render(<Index />));
    expect(await screen.findByText('Dispatches List')).toBeInTheDocument();
  });

  it('renders correctly with not found dispatch data', async () => {
    mockadapter.onGet(API_URLS.DISPATCH).reply(400);

    act(() => render(<Index />));
    expect(await screen.findByText('Dispatches List')).toBeInTheDocument();
  });
});
