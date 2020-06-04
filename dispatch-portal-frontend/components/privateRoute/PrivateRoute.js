import ServerCookie from 'next-cookies';
import React, { Component } from 'react';
import { Routes } from '../../config/routes';
import { TOKEN_STORAGE_KEY } from '../../services/auth/login.service';

export function privateRoute(WrappedComponent) {
  return class extends Component {
    static async getInitialProps(ctx) {
      const token = ServerCookie(ctx)[TOKEN_STORAGE_KEY];

      if (!token) {
        ctx.res.writeHead(302, {
          Location: `${Routes.LOGIN()}?redirected=true`
        });
        ctx.res.end();
      }
      const initialProps = { authToken: token };
      if (WrappedComponent.getInitialProps) {
        return WrappedComponent.getInitialProps(initialProps);
      }
      return initialProps;
    }

    render() {
      return <WrappedComponent {...this.props} />;
    }
  };
}
