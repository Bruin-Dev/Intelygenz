import { locationInAdapter } from './location.adapter';
import { getLocationByTicketIdMock } from '../mocks/data/location/location.mock';

describe('location adapter tests', () => {
  it('should match the snapshot', () => {
    expect(locationInAdapter(getLocationByTicketIdMock)).toMatchSnapshot();
  });
});
