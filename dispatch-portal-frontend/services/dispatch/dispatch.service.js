import { API_URLS } from '../api.config';
import axiosInstance from '../api';
import {
  dispatchLitInAdapter,
  dispatchLitInAdapterGeAll,
  dispatchLitOutAdapter
} from './lit-dispatch.adapter';
import {
  dispatchCtsInAdapter,
  dispatchCtsInAdapterGeAll,
  dispatchCtsOutAdapter
} from './cts-dispatch.adapter';
import { config } from '../../config/config';

export class DispatchService {
  constructor(axiosAuxI = axiosInstance) {
    this.axiosI = axiosAuxI;
  }

  async getAllByVendor(vendor) {
    try {
      if (config.VENDORS.LIT === vendor) {
        const res = await this.axiosI.get(API_URLS.DISPATCH_LIT);

        return res.data.list_dispatch.map(dispatch =>
          dispatchLitInAdapterGeAll({
            ...dispatch,
            vendor: res.data.vendor
          })
        );
      }

      if (config.VENDORS.CTS === vendor) {
        const res = await this.axiosI.get(API_URLS.DISPATCH_CTS);

        return res.data.list_dispatch.map(dispatch =>
          dispatchCtsInAdapterGeAll({
            ...dispatch,
            vendor: res.data.vendor
          })
        );
      }
    } catch (error) {
      return this.captureErrorGeneric(error);
    }
  }

  async getAll() {
    const responseLit = await this.getAllByVendor(config.VENDORS.LIT);
    const responseCts = await this.getAllByVendor(config.VENDORS.CTS);

    // Fails both calls
    if (responseLit.error && responseCts.error) {
      return {
        error: `${responseCts.error} && ${responseLit.error}`
      };
    }

    // Lit error
    if (responseLit.error) {
      return {
        data: responseCts,
        ...responseLit
      };
    }

    // Cts error
    if (responseCts.error) {
      return {
        data: responseLit,
        ...responseCts
      };
    }

    // Success
    return {
      data: [...responseLit, ...responseCts]
    };
  }

  async newDispatch(data, vendor) {
    try {
      let res;
      if (config.VENDORS.LIT === vendor) {
        res = await this.axiosI.post(
          API_URLS.DISPATCH_LIT,
          dispatchLitOutAdapter(data)
        );

        return res;
      }

      if (config.VENDORS.CTS === vendor) {
        res = await this.axiosI.post(
          API_URLS.DISPATCH_CTS,
          dispatchCtsOutAdapter(data)
        );

        return res;
      }

      return { error: 'Not vendor selected' };
    } catch (error) {
      return this.captureErrorGeneric(error);
    }
  }

  async get(id, vendor) {
    try {
      let res;
      if (config.VENDORS.LIT === vendor) {
        res = await this.axiosI.get(`${API_URLS.DISPATCH_LIT}/${id}`);

        return dispatchLitInAdapter(res.data);
      }

      if (config.VENDORS.CTS === vendor) {
        res = await this.axiosI.get(`${API_URLS.DISPATCH_CTS}/${id}`);

        return dispatchCtsInAdapter(res.data);
      }
      return { error: 'Not vendor selected' };
    } catch (error) {
      return this.captureErrorGeneric(error);
    }
  }

  async update(id, vendor, body) {
    try {
      let res;
      if (config.VENDORS.LIT === vendor) {
        res = await this.axiosI.patch(`${API_URLS.DISPATCH_LIT}/${id}`, body);

        return dispatchLitInAdapter(res.data);
      }

      if (config.VENDORS.CTS === vendor) {
        res = await this.axiosI.patch(`${API_URLS.DISPATCH_CTS}/${id}`, body);

        return dispatchCtsInAdapter(res.data);
      }
      return { error: 'Not vendor selected' };
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
