import React from 'react';
import { render, act, fireEvent, screen } from '@testing-library/react';
import Login from './login';
import { withTestRouter } from '../components/menu/Menu.test';
import { Routes } from '../config/routes';

describe('LOGIN PAGE tests', () => {
  it('renders correctly', () => {
    const { queryByTestId } = render(<Login />);
    expect(queryByTestId('login-page-component')).toBeTruthy();
  });

  it('Check required fields', async () => {
    render(<Login />);
    const button = screen.getByText('Login');

    fireEvent.click(button);

    expect(await screen.findByText('Password is required')).toBeInTheDocument();
    expect(await screen.findByText('Required')).toBeInTheDocument();
  });

  it('Check required incorrect fields', async () => {
    render(<Login />);
    const button = screen.getByText('Login');

    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'example@example.com' }
    });
    fireEvent.change(screen.getByPlaceholderText('******************'), {
      target: { value: '12345' }
    });

    fireEvent.click(button);

    expect(
      await screen.findByText('The data entered is not correct.')
    ).toBeInTheDocument();
  });

  /*
  it('Check required correct fields and submit', async () => {
    // Todo: mock login service
    const push = jest.fn();

    const component = withTestRouter(<Login />, {
      push,
      pathname: '/login',
      asPath: '/login'
    });

    const { getByText, getByPlaceholderText } = render(component);
    const button = getByText('Login');
    await act(async () => {
      fireEvent.change(getByPlaceholderText('Email'), {
        target: { value: 'mettel@mettel.com' }
      });
      fireEvent.change(getByPlaceholderText('******************'), {
        target: { value: '1234' }
      });

      fireEvent.click(button);
    });

    expect(push).toHaveBeenCalledWith(`${Routes.BASE()}?redirect=?true`);
  }); */
});
