import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { DispatchService } from './dispatch.service';
import { API_URLS } from '../api.config';
import { dispatchList } from '../mocks/list-dispatch.mock';
import {
  formDataNewDispatch,
  mocksInAdapterLitSingleDispatchResult
} from '../mocks/new-dispatch.mock';
import { mockLitSingleDispatch } from '../mocks/single-dispatch.mock';

describe('dispatch service tests', () => {
  const axiosIMocksTest = axios.create();
  let mockadapter;

  beforeEach(() => {
    mockadapter = new MockAdapter(axiosIMocksTest);
  });

  afterEach(() => {
    mockadapter.reset();
  });

  it('fetches getAll successfully data from an API', async () => {
    mockadapter.onGet(API_URLS.DISPATCH).reply(200, {
      vendor: 'lit',
      list_dispatch: [dispatchList.data[0]]
    });
    const expectedResult = [
      {
        dateDispatch: '2015-01-01',
        details: {
          fieldEngineer: '===not set===',
          fieldEngineerContactNumber: '===not set===',
          information: 'ScopeOfWork',
          instructions: '1',
          materials: '1',
          serviceType: '===not set===',
          specialMaterials: '===not set==='
        },
        hardTimeDispatch: '===not set===',
        hardTimeZone: '===not set===',
        id: 'DIS17918',
        mettelId: '0',
        onSiteContact: {
          city: 'Citizville',
          name: 'Rajat 11111',
          phoneNumber: '===not set===',
          site: 'Primary Citiscape',
          state: 'NY',
          street: '124 Spring street',
          zip: '12345'
        },
        requester: {
          department: '1',
          departmentPhoneNumber: '===not set===',
          email: 'pkamath@mettel.net',
          groupEmail: '===not set===',
          name: 'pkamath',
          phoneNumber: '===not set==='
        },
        slaLevel: '===not set===',
        status: 'New Dispatch',
        timeDispatch: '===not set===',
        timeZone: '2',
        turnUp: '===not set===',
        vendor: 'lit'
      }
    ];

    const res = await new DispatchService(axiosIMocksTest).getAll();
    expect(res).toMatchObject({ data: expectedResult });
  });

  it('fetches getAll error 503 from an API', async () => {
    mockadapter.onGet(API_URLS.DISPATCH).reply(503);

    const res = await new DispatchService(axiosIMocksTest).getAll();

    expect(res).toMatchObject({
      error: 'Request failed with status code 503'
    });
  });

  it('fetches newDispacth successfully data from an API', async () => {
    const apiResponseMock = { id: 123 };
    mockadapter.onPost(API_URLS.DISPATCH).reply(204, apiResponseMock);

    const res = await new DispatchService(axiosIMocksTest).newDispatch(
      formDataNewDispatch
    ); // Todo: review data

    expect(res).toMatchObject({ data: apiResponseMock });
  });

  it('fetches newDispacth error 400 from an API', async () => {
    mockadapter.onPost(API_URLS.DISPATCH).reply(400);

    const res = await new DispatchService(axiosIMocksTest).newDispatch(
      formDataNewDispatch
    ); // Todo: review data;

    expect(res).toMatchObject({
      error: 'Request failed with status code 400'
    });
  });

  it('fetches get successfully data from an API', async () => {
    mockadapter
      .onGet(new RegExp(`${API_URLS.DISPATCH}/*`))
      .reply(200, mockLitSingleDispatch);

    const res = await new DispatchService(axiosIMocksTest).get(
      mockLitSingleDispatch.id
    );

    expect(res).toMatchObject(mocksInAdapterLitSingleDispatchResult);
  });

  it('fetches get error 400 from an API', async () => {
    mockadapter.onGet(new RegExp(`${API_URLS.DISPATCH}/*`)).reply(400);

    const res = await new DispatchService(axiosIMocksTest).get(
      mockLitSingleDispatch.id
    );

    expect(res).toMatchObject({
      error: 'Request failed with status code 400'
    });
  });

  it('fetches uploadFiles successfully data from an API', async () => {
    mockadapter.onPost(API_URLS.UPLOAD_FILES).reply(204);

    const res = await new DispatchService(axiosIMocksTest).uploadFiles(
      'DIS5446',
      {}
    );

    expect(res).toBe(true);
  });

  it('fetches uploadFiles error 404 from an API', async () => {
    mockadapter.onPost(API_URLS.UPLOAD_FILES).reply(404);

    const res = await new DispatchService(axiosIMocksTest).uploadFiles(
      'DIS5446',
      {}
    );

    expect(res).toMatchObject({
      error: 'Request failed with status code 404'
    });
  });
});
