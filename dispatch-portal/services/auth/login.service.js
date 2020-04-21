import { API_URLS, axiosInstance } from '../api';

export const TOKEN_STORAGE_KEY = 'dispathPortal.authToken';

export const loginService = {
  postLogin: async formData => {
    const data = new URLSearchParams(formData);
    const res = await axiosInstance.post(API_URLS.LOGIN, data);

    if (res.error) {
      return res.error;
    }
    if (!res.data || !res.data.token) {
      return 'Something went wrong!';
    }

    // Fake: Todo: delete when service enabled
    if (
      !(formData.email === 'mettel@mettel.com' && formData.password === '1234')
    ) {
      return { error: 'Login incorrect' };
    }

    const { token } = res.data;
    document.cookie = `${TOKEN_STORAGE_KEY}=${token}; path=/`;
    return res;
  }
};
