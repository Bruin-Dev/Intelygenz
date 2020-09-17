import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { LocationService } from './location.service';
import { getLocationByTicketIdMock } from '../mocks/data/location/location.mock';
import { API_URLS } from '../api.config';

describe('location service tests', () => {
  const ticketIdMock = 'foo';
  const axiosIMocksTest = axios.create();
  let mockadapter;

  beforeEach(() => {
    mockadapter = new MockAdapter(axiosIMocksTest);
  });

  afterEach(() => {
    mockadapter.reset();
  });

  describe('getLocationByTicketId', () => {
    it('should match the snapshot', async () => {
      // Arrange.
      mockadapter
        .onGet(new RegExp(`${API_URLS.GET_LOCATION_BY_TICKET_ID}/*`))
        .reply(200, getLocationByTicketIdMock);

      // Act.
      const response = await new LocationService(
        axiosIMocksTest
      ).getLocationByTicketId(ticketIdMock);

      // Assert.
      expect(response).toMatchSnapshot();
    });

    it('should return an error if the service fail', async () => {
      // Arrange.
      mockadapter
        .onGet(new RegExp(`${API_URLS.GET_LOCATION_BY_TICKET_ID}/*`))
        .reply(404);

      // Act.
      const response = await new LocationService(
        axiosIMocksTest
      ).getLocationByTicketId(ticketIdMock);

      // Assert.
      expect(response).toMatchSnapshot();
    });
  });
});
