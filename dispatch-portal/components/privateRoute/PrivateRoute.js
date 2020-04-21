import ServerCookie from 'next-cookies';
import React, { Component } from 'react';
import { TOKEN_STORAGE_KEY } from '../../services/auth/login.service';

export function privateRoute(WrappedComponent) {
  return class extends Component {
    static async getInitialProps(ctx) {
      const token = ServerCookie(ctx)[TOKEN_STORAGE_KEY];
      const initialProps = { authToken: token };
      if (!token) {
        ctx.res.writeHead(302, {
          Location: '/login?redirected=true'
        });
        ctx.res.end();
      }
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
