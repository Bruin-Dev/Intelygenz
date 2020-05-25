import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useForm } from 'react-hook-form';
import ServerCookie from 'next-cookies';
import {
  loginService,
  TOKEN_STORAGE_KEY
} from '../services/auth/login.service';
import { Routes } from '../config/routes';
import Loading from '../components/loading/Loading';
import './login.scss';

function Login() {
  const router = useRouter();
  const { handleSubmit, register, errors } = useForm();
  const [response, setResponse] = useState({
    error: false,
    data: false
  });
  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async values => {
    setIsLoading(true);
    const loginResponse = await loginService.postLogin(values);
    setResponse({ ...response, ...loginResponse });

    // Redirect to dashboard page
    if (loginResponse.data) {
      router.push(`${Routes.BASE()}?redirect=?true`);
    } else {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-wrapper">
      <div className="flex mb-4">
        <div className="sm:w-full md:w-1/3 ml-auto mr-auto h-12">
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4"
            data-test-id="login-form"
          >
            <div className="mb-4">
              <label
                className="block text-gray-700 text-sm font-bold mb-2"
                htmlFor="email"
              >
                Email
                <input
                  ref={register({
                    required: 'Required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i,
                      message: 'invalid email address'
                    }
                  })}
                  className={
                    errors.email
                      ? `shadow appearance-none border border-red-500 rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline`
                      : `shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline`
                  }
                  id="email"
                  placeholder="Email"
                  name="email"
                />
                {errors.email && (
                  <p
                    className="text-red-500 text-xs italic"
                    data-test-id="error-email-login-form"
                  >
                    {errors.email.message}
                  </p>
                )}
              </label>
            </div>
            <div className="mb-6">
              <label
                className="block text-gray-700 text-sm font-bold mb-2"
                htmlFor="password"
              >
                Password
                <input
                  className={
                    errors.password
                      ? `shadow appearance-none border border-red-500 rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline`
                      : `shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline`
                  }
                  id="password"
                  type="password"
                  placeholder="******************"
                  ref={register({
                    required: 'Required'
                  })}
                  name="password"
                />
                {errors.password && (
                  <p
                    className="text-red-500 text-xs italic"
                    data-test-id="error-password-login-form"
                  >
                    Password is required
                  </p>
                )}
              </label>
            </div>
            <div className="flex items-center justify-between">
              {response.error && (
                <p
                  className="text-red-500 text-xs italic"
                  data-test-id="error-api-login-form"
                >
                  The data entered is not correct.
                </p>
              )}
              {isLoading ? (
                <Loading />
              ) : (
                <button
                  type="submit"
                  className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  data-test-id="login-submit"
                >
                  Login
                </button>
              )}
            </div>
          </form>
        </div>
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
