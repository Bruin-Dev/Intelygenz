import React from 'react';
import { render, fireEvent, screen, act } from '@testing-library/react';
import MockAdapter from 'axios-mock-adapter';
import NewDispatch from '../pages/new-dispatch';
import axiosI from '../services/api';
import { API_URLS } from '../services/api.config';
import { withTestRouter } from '../components/menu/Menu.test';
import { Routes } from '../config/routes';

describe('NEW DISPATCH PAGE tests', () => {
  let mockadapter;

  beforeEach(() => {
    mockadapter = new MockAdapter(axiosI);
  });

  afterEach(() => {
    mockadapter.reset();
  });

  it('renders correctly', () => {
    const { queryByTestId } = render(<NewDispatch />);
    expect(queryByTestId('newDispatch-page-component')).toBeTruthy();
  });

  it('show others fields by vendor', () => {
    const { getByTestId } = render(<NewDispatch />);
    const checkboxCTS = getByTestId('CTS-checkbox');

    fireEvent.click(checkboxCTS);

    expect(getByTestId('cts-field')).toBeTruthy();
  });

  it('show validation errors', async () => {
    render(<NewDispatch />);
    const button = screen.getByText('Submit');

    act(() => {
      fireEvent.change(screen.getByTestId('emailRequester'), {
        target: { value: 'example' }
      });

      fireEvent.click(button);
    });

    expect(
      await screen.findByText('Incorrect format: example@example.com')
    ).toBeInTheDocument();
  });

  it('check submit error', async () => {
    mockadapter
      .onGet(new RegExp(`${API_URLS.DISPATCH}/*`))
      .reply(400, { error: 'Error!' });
    render(<NewDispatch />);
    const button = screen.getByText('Submit');

    await act(async () => {
      fireEvent.change(screen.getByTestId('dateDispatch'), {
        target: { value: '1992-05-05' }
      });

      fireEvent.click(screen.getByTestId('LIT-checkbox'));
      fireEvent.change(screen.getByTestId('mettelId'), {
        target: { value: '23434423' }
      });

      fireEvent.change(screen.getByTestId('owner'), {
        target: { value: 'JESSS' }
      });
      fireEvent.change(screen.getByTestId('address1'), {
        target: { value: 'AV ESPAÑA 40' }
      });
      fireEvent.change(screen.getByTestId('address2'), {
        target: { value: 'LAS ROZAS MD' }
      });
      fireEvent.change(screen.getByTestId('city'), {
        target: { value: 'MADRID' }
      });

      fireEvent.change(screen.getByTestId('zip'), {
        target: { value: '87978' }
      });
      fireEvent.change(screen.getByTestId('firstName'), {
        target: { value: 'ROBER' }
      });
      fireEvent.change(screen.getByTestId('lastName'), {
        target: { value: 'JONSON' }
      });
      fireEvent.change(screen.getByTestId('phoneNumber'), {
        target: { value: '+1 587897524' }
      });

      fireEvent.change(screen.getByTestId('issues'), {
        target: { value: 'kjnskjdn adsk sdknaskjdn' }
      });
      fireEvent.change(screen.getByTestId('materials'), {
        target: { value: 'akndjknas dkjnadsjklnas jkdn' }
      });
      fireEvent.change(screen.getByTestId('instructions'), {
        target: { value: 'nkjadn kjandsjkdkl nkasdln' }
      });
      fireEvent.change(screen.getByTestId('firstNameRequester'), {
        target: { value: 'jacson' }
      });
      fireEvent.change(screen.getByTestId('lastNameRequester'), {
        target: { value: 'lucjer' }
      });

      fireEvent.change(screen.getByTestId('phoneNumberRequester'), {
        target: { value: '+1 587897524' }
      });
      fireEvent.change(screen.getByTestId('emailRequester'), {
        target: { value: 'example1@exmaple.com' }
      });

      fireEvent.click(button);
    });

    expect(
      await screen.getByTestId('error-new-dispatch-page')
    ).toBeInTheDocument();
  });

  /*
  Todo: falta ir a los detalles
  it('check submit sucessfull and go to detail route', async () => {
    const push = jest.fn();

    mockadapter
      .onGet(new RegExp(`${API_URLS.DISPATCH}/*`))
      .reply(204, { id: '124' });

    const component = withTestRouter(<NewDispatch />, {
      push,
      pathname: '/new-dispatch',
      asPath: '/new-dispatch'
    });
    render(component);
    const button = screen.getByText('Submit');

    await act(async () => {
      fireEvent.change(screen.getByTestId('dateDispatch'), {
        target: { value: '1992-05-05' }
      });

      fireEvent.click(screen.getByTestId('LIT-checkbox'));
      fireEvent.change(screen.getByTestId('mettelId'), {
        target: { value: '23434423' }
      });

      fireEvent.change(screen.getByTestId('owner'), {
        target: { value: 'JESSS' }
      });
      fireEvent.change(screen.getByTestId('address1'), {
        target: { value: 'AV ESPAÑA 40' }
      });
      fireEvent.change(screen.getByTestId('address2'), {
        target: { value: 'LAS ROZAS MD' }
      });
      fireEvent.change(screen.getByTestId('city'), {
        target: { value: 'MADRID' }
      });

      fireEvent.change(screen.getByTestId('zip'), {
        target: { value: '87978' }
      });
      fireEvent.change(screen.getByTestId('firstName'), {
        target: { value: 'ROBER' }
      });
      fireEvent.change(screen.getByTestId('lastName'), {
        target: { value: 'JONSON' }
      });
      fireEvent.change(screen.getByTestId('phoneNumber'), {
        target: { value: '+1 587897524' }
      });

      fireEvent.change(screen.getByTestId('issues'), {
        target: { value: 'kjnskjdn adsk sdknaskjdn' }
      });
      fireEvent.change(screen.getByTestId('materials'), {
        target: { value: 'akndjknas dkjnadsjklnas jkdn' }
      });
      fireEvent.change(screen.getByTestId('instructions'), {
        target: { value: 'nkjadn kjandsjkdkl nkasdln' }
      });
      fireEvent.change(screen.getByTestId('firstNameRequester'), {
        target: { value: 'jacson' }
      });
      fireEvent.change(screen.getByTestId('lastNameRequester'), {
        target: { value: 'lucjer' }
      });

      fireEvent.change(screen.getByTestId('phoneNumberRequester'), {
        target: { value: '+1 587897524' }
      });
      fireEvent.change(screen.getByTestId('emailRequester'), {
        target: { value: 'example1@exmaple.com' }
      });

      fireEvent.click(button);
    });

    expect(push).toHaveBeenCalledWith(`${Routes.NEW_DISPATCH()}/124`);
  }); */
});
