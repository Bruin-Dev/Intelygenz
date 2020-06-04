import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { LoginService } from './login.service';
import { API_URLS } from '../api.config';
import { userLoginSucess } from '../mocks/userData.mocks';

describe('login service tests', () => {
  const axiosIMocksTest = axios.create();
  let mockadapter;
  const apiResponse = {
    token: 'XXXX-fake-token'
  };

  beforeEach(() => {
    mockadapter = new MockAdapter(axiosIMocksTest);
  });

  afterEach(() => {
    mockadapter.reset();
  });

  it('fetches login successfully data from an API', async () => {
    mockadapter.onPost(API_URLS.LOGIN).reply(200, apiResponse);

    const res = await new LoginService(axiosIMocksTest).postLogin(
      userLoginSucess
    );
    expect(res).toMatchObject({ data: apiResponse });
  });

  it('fetches login incorrect data from an API', async () => {
    mockadapter.onPost(API_URLS.LOGIN).reply(200, apiResponse);

    const res = await new LoginService(axiosIMocksTest).postLogin({
      email: 'example@example.com',
      password: '1234'
    });
    expect(res).toMatchObject({ error: 'Login incorrect' });
  });

  it('fetches login token error data from an API', async () => {
    mockadapter.onPost(API_URLS.LOGIN).reply(200, {
      tokenFail: 'XXXx-5885'
    });

    const res = await new LoginService(axiosIMocksTest).postLogin(
      userLoginSucess
    );
    expect(res).toMatchObject({ error: 'Token error: Something went wrong!' });
  });

  it('fetches login error data from an API', async () => {
    mockadapter.onPost(API_URLS.LOGIN).reply(400);

    const res = await new LoginService(axiosIMocksTest).postLogin(
      userLoginSucess
    );

    expect(res).toMatchObject({ error: 'Request failed with status code 400' });
  });
});
