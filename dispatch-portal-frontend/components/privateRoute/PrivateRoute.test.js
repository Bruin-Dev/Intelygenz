import React from 'react';
import { render } from '@testing-library/react';
import { toBeInTheDocument } from '@testing-library/jest-dom';

import { privateRoute } from './PrivateRoute';
import { Routes } from '../../config/routes';
import { TOKEN_STORAGE_KEY } from '../../services/auth/login.service';

describe('PrivateRoute Component tests', () => {
  const MockApp = () => <p>Hello from your Mock App</p>;

  const MockWithHOC = privateRoute(MockApp);

  it('renders correctly', () => {
    const { getByText } = render(<MockWithHOC />);
    expect(getByText(/Hello from your Mock App/i)).toBeInTheDocument();
  });

  it('check redirect correctly to login', async () => {
    const mockWriteHead = jest.fn();
    await MockWithHOC.getInitialProps({
      res: {
        writeHead: mockWriteHead,
        end: jest.fn()
      }
    });

    expect(mockWriteHead).toHaveBeenCalledWith(302, {
      Location: `${Routes.LOGIN()}?redirected=true`
    });
  });

  /* it('check token', async () => {
    const cookie = 'XXX-token-cookie';
    const mockCookie = `${TOKEN_STORAGE_KEY}=${cookie}`;
    const props = await MockWithHOC.getInitialProps({
      res: {
        writeHead: jest.fn(),
        end: jest.fn()
      },
      req: {
        headers: {
          cookie: mockCookie
        }
      }
    });

    expect(props).toEqual({
      authToken: cookie
    });
  }); */
});
