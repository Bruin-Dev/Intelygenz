import React, { useState } from 'react';
import { useRouter } from 'next/router';
import ServerCookie from 'next-cookies';
import {
  loginService,
  TOKEN_STORAGE_KEY
} from '../services/auth/login.service';
import Loading from '../components/loading/Loading';
import { Routes } from '../config/routes';
import './login.scss';

function Login() {
  const router = useRouter();

  const initialInputsValues = {
    email: 'example@example.com',
    password: '****'
  };

  const initialResponseValues = {
    error: false,
    data: false
  };

  const [inputs, setInputs] = useState(initialInputsValues);
  const [response, setResponse] = useState(initialResponseValues);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async e => {
    e.preventDefault();
    setIsLoading(true);
    const loginResponse = await loginService.postLogin(inputs);
    setResponse({ ...response, ...loginResponse });

    // Redirect to dashboard page
    if (loginResponse.data) {
      router.push(`${Routes.BASE()}?redirect=?true`); // Todo not working, problem with webpack, in build pro everythings is "OK"
      // eslint-disable-next-line no-restricted-globals
      location.reload(); // Todo review parche
    } else {
      setIsLoading(false);
    }
  };

  const handleInputChange = e => {
    e.persist();

    // Recovery initial status for errors
    if (initialResponseValues.error !== response.error) {
      setResponse(initialResponseValues);
    }

    setInputs({
      ...inputs,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="login-wrapper">
      <div className="login-card">
        <p className="title">LOGIN</p>
        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email">
              Email <br />
              <input
                type="email"
                id="email"
                name="email"
                // className="danger - warning - success - disabled"
                onChange={handleInputChange}
                value={inputs.email}
              />
            </label>
          </div>
          <div>
            <label htmlFor="password">
              Password <br />
              <input
                type="password"
                id="password"
                name="password"
                onChange={handleInputChange}
                value={inputs.password}
              />
            </label>
          </div>
          {response.error && <p className="error">Error!</p>}
          {isLoading ? (
            <Loading />
          ) : (
            <button className="login" type="submit">
              Login
            </button>
          )}
        </form>
      </div>
    </div>
  );
}

Login.getInitialProps = async ctx => {
  const token = ServerCookie(ctx)[TOKEN_STORAGE_KEY];
  const initialProps = { authToken: token };
  if (token) {
    ctx.res.writeHead(302, {
      Location: '/?redirected=true'
    });
    ctx.res.end();
  }
  return initialProps;
};

export default Login;
