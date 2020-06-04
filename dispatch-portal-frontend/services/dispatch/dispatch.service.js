import { API_URLS } from '../api.config';
import axiosInstance from '../api';
import {
  dispatchLitInAdapter,
  dispatchLitOutAdapter
} from './dispatch.adapter';

export class DispatchService {
  constructor(axiosAuxI = axiosInstance) {
    this.axiosI = axiosAuxI;
  }

  async getAll() {
    try {
      const res = await this.axiosI.get(API_URLS.DISPATCH);

      return {
        data: res.data.list_dispatch.map(dispatch =>
          dispatchLitInAdapter({ ...dispatch, vendor: res.data.vendor })
        )
      };
    } catch (error) {
      return this.captureErrorGeneric(error);
    }
  }

  async newDispatch(data) {
    try {
      const res = await this.axiosI.post(
        API_URLS.DISPATCH,
        dispatchLitOutAdapter(data)
      );

      return res;
    } catch (error) {
      return this.captureErrorGeneric(error);
    }
  }

  async get(id) {
    try {
      const res = await this.axiosI.get(`${API_URLS.DISPATCH}/${id}`);

      return dispatchLitInAdapter(res.data);
    } catch (error) {
      return this.captureErrorGeneric(error);
    }
  }

  async uploadFiles(id, data) {
    try {
      const res = await this.axiosI.post(API_URLS.UPLOAD_FILES, data);

      return true;
    } catch (error) {
      return this.captureErrorGeneric(error);
    }
  }

  // eslint-disable-next-line class-methods-use-this
  captureErrorGeneric(error) {
    return { error: error.message };
  }
}
