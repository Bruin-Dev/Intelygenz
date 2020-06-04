import { API_URLS } from '../api.config';
import axiosInstanceMocks from '../mocks/mocks';

export const TOKEN_STORAGE_KEY = 'dispathPortal.authToken';

export class LoginService {
  constructor(axiosAuxI = axiosInstanceMocks) {
    // Todo: delete when service enabled, change for: axiosInstance
    this.axiosI = axiosAuxI;
  }

  async postLogin(formData) {
    try {
      const data = new URLSearchParams(formData);

      // Fake: Todo: delete when service enabled
      if (
        !(
          formData.email === 'mettel@mettel.com' && formData.password === '1234'
        )
      ) {
        return { error: 'Login incorrect' };
      }

      const res = await this.axiosI.post(API_URLS.LOGIN, data);

      if (!res.data || !res.data.token) {
        return { error: 'Token error: Something went wrong!' };
      }

      const { token } = res.data;
      document.cookie = `${TOKEN_STORAGE_KEY}=${token}; path=/`;
      return res;
    } catch (error) {
      return { error: error.message };
    }
  }
}
