import { Routes } from './routes';

describe('check routes file', () => {
  const OLD_ENV = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = { ...OLD_ENV };
    process.env.BASE_PATH = '/';
    delete process.env.NODE_ENV;
  });

  afterEach(() => {
    process.env = OLD_ENV;
  });

  it('check route creation', () => {
    expect(Routes.BASE()).toEqual('undefined'); // Todo: ver como pasar process.env
    expect(Routes.DISPATCH()).toEqual('undefineddispatch');
    expect(Routes.NEW_DISPATCH()).toEqual('undefinednew-dispatch');
    expect(Routes.LOGIN()).toEqual('undefinedlogin');
  });
});
