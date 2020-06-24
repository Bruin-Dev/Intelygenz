import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { DispatchService } from './dispatch.service';
import { API_URLS } from '../api.config';
import { dispatchLitList } from '../mocks/data/lit/list-dispatch.mock';
import { formDataNewDispatch } from '../mocks/data/new-dispatch.mock';
import { mockLitSingleDispatch } from '../mocks/data/lit/single-dispatch.mock';
import { mocksInAdapterLitSingleDispatchResult } from '../mocks/data/lit/result-adapter-in-dispatch.datatest';
import { dispatchCtsList } from '../mocks/data/cts/list-dispatch.mock';
import { config } from '../../config/config';
import { mockCtsSingleDispatch } from '../mocks/data/cts/single-dispatch.mock';
import { mocksInAdapterCtsSingleDispatchResult } from '../mocks/data/cts/result-adapter-in-dispatch.datatest';
import { dispatchCtsInAdapter } from './cts-dispatch.adapter';
import { dispatchLitInAdapter } from './lit-dispatch.adapter';

describe('dispatch service tests', () => {
  const axiosIMocksTest = axios.create();
  let mockadapter;

  beforeEach(() => {
    mockadapter = new MockAdapter(axiosIMocksTest);
  });

  afterEach(() => {
    mockadapter.reset();
  });

  /** ***
   *
   * GET ALL
   * * */
  it('fetch getAll: successfully data from an API(CTS &  LIT OK)', async () => {
    mockadapter.onGet(API_URLS.DISPATCH_LIT).reply(200, {
      vendor: 'lit',
      list_dispatch: [dispatchLitList.data[0]]
    });
    mockadapter.onGet(API_URLS.DISPATCH_CTS).reply(200, {
      vendor: 'cts',
      list_dispatch: [dispatchCtsList.data[0]]
    });
    const expectedResult = [
      dispatchLitInAdapter({ vendor: 'lit', ...dispatchLitList.data[0] }),
      dispatchCtsInAdapter({ vendor: 'cts', ...dispatchCtsList.data[0] })
    ];

    const res = await new DispatchService(axiosIMocksTest).getAll();

    expect(res).toMatchObject({ data: expectedResult });
  });

  it('fetch getAll: one of the calls fails(CTS)', async () => {
    mockadapter.onGet(API_URLS.DISPATCH_LIT).reply(404);
    mockadapter.onGet(API_URLS.DISPATCH_CTS).reply(200, {
      vendor: 'cts',
      list_dispatch: [dispatchCtsList.data[0]]
    });
    const expectedResult = [
      dispatchCtsInAdapter({ vendor: 'cts', ...dispatchCtsList.data[0] })
    ];

    const res = await new DispatchService(axiosIMocksTest).getAll();

    expect(res).toMatchObject({
      data: expectedResult,
      error: 'Request failed with status code 404'
    });
  });
  it('fetch getAll: one of the calls fails(LIT)', async () => {
    mockadapter.onGet(API_URLS.DISPATCH_CTS).reply(404);
    mockadapter.onGet(API_URLS.DISPATCH_LIT).reply(200, {
      vendor: 'lit',
      list_dispatch: [dispatchLitList.data[0]]
    });
    const expectedResult = [
      dispatchLitInAdapter({ vendor: 'lit', ...dispatchLitList.data[0] })
    ];

    const res = await new DispatchService(axiosIMocksTest).getAll();

    expect(res).toMatchObject({
      data: expectedResult,
      error: 'Request failed with status code 404'
    });
  });

  it('fetch getAll: error 503 from both API', async () => {
    mockadapter.onGet(API_URLS.DISPATCH_LIT).reply(503);
    mockadapter.onGet(API_URLS.DISPATCH_CTS).reply(503);

    const res = await new DispatchService(axiosIMocksTest).getAll();

    expect(res).toMatchObject({
      error:
        'Request failed with status code 503 && Request failed with status code 503'
    });
  });

  /** ***
   *
   * GET SINGLE DISPATCH
   * * */
  it('fetch get: successfully data from an API(LIT)', async () => {
    mockadapter
      .onGet(new RegExp(`${API_URLS.DISPATCH_LIT}/*`))
      .reply(200, mockLitSingleDispatch);

    const res = await new DispatchService(axiosIMocksTest).get(
      mockLitSingleDispatch.id,
      config.VENDORS.LIT
    );

    expect(res).toMatchObject(mocksInAdapterLitSingleDispatchResult);
  });

  it('fetch get: successfully data from an API(CTS)', async () => {
    mockadapter
      .onGet(new RegExp(`${API_URLS.DISPATCH_CTS}/*`))
      .reply(200, mockCtsSingleDispatch);

    const res = await new DispatchService(axiosIMocksTest).get(
      mockCtsSingleDispatch.id,
      config.VENDORS.CTS
    );

    expect(res).toMatchObject(mocksInAdapterCtsSingleDispatchResult);
  });

  it('fetch get: error 400 from an API', async () => {
    mockadapter.onGet(new RegExp(`${API_URLS.DISPATCH_LIT}/*`)).reply(400);

    const res = await new DispatchService(axiosIMocksTest).get(
      mockLitSingleDispatch.id,
      config.VENDORS.LIT
    );

    expect(res).toMatchObject({
      error: 'Request failed with status code 400'
    });
  });

  it('fetches get: but not vendor selected', async () => {
    mockadapter.onGet(new RegExp(`${API_URLS.DISPATCH_LIT}/*`)).reply(400);

    const res = await new DispatchService(axiosIMocksTest).get(
      mockLitSingleDispatch.id,
      'XXX'
    );

    expect(res).toMatchObject({
      error: 'Not vendor selected'
    });
  });

  /** ***
   *
   * NEW DISPATCH
   * * */
  it('fetch newDispacth: successfully data from an API(LIT)', async () => {
    const apiResponseMock = { id: 123 };
    mockadapter.onPost(API_URLS.DISPATCH_LIT).reply(204, apiResponseMock);

    const res = await new DispatchService(axiosIMocksTest).newDispatch(
      formDataNewDispatch,
      config.VENDORS.LIT
    );

    expect(res).toMatchObject({ data: apiResponseMock });
  });
  it('fetch newDispacth: successfully data from an API(CTS)', async () => {
    const apiResponseMock = { id: 123 };
    mockadapter.onPost(API_URLS.DISPATCH_CTS).reply(204, apiResponseMock);

    const res = await new DispatchService(axiosIMocksTest).newDispatch(
      formDataNewDispatch,
      config.VENDORS.CTS
    );

    expect(res).toMatchObject({ data: apiResponseMock });
  });

  it('fetches newDispacth error 400 from an API', async () => {
    mockadapter.onPost(API_URLS.DISPATCH_LIT).reply(400);

    const res = await new DispatchService(axiosIMocksTest).newDispatch(
      formDataNewDispatch,
      config.VENDORS.LIT
    );

    expect(res).toMatchObject({
      error: 'Request failed with status code 400'
    });
  });

  it('fetches newDispacth: but not vendor selected', async () => {
    mockadapter.onPost(API_URLS.DISPATCH_LIT).reply(400);

    const res = await new DispatchService(axiosIMocksTest).newDispatch(
      formDataNewDispatch,
      'XXX'
    );

    expect(res).toMatchObject({
      error: 'Not vendor selected'
    });
  });

  /** ***
   *
   * UPLOAD FILES
   * * */
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
