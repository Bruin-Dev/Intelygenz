import { API_URLS } from '../api.config';
import axiosInstance from '../api';
import { locationInAdapter } from './location.adapter';

export class LocationService {
  constructor(axiosAuxI = axiosInstance) {
    this.axiosI = axiosAuxI;
  }

  async getLocationByTicketId(ticketId) {
    try {
      const res = await this.axiosI.get(
        `${API_URLS.GET_LOCATION_BY_TICKET_ID}/${ticketId}`
      );
      return locationInAdapter(res.data);
    } catch (error) {
      return this.captureErrorGeneric(error);
    }
  }

  // eslint-disable-next-line class-methods-use-this
  captureErrorGeneric(error) {
    return { error: error.message };
  }
}
