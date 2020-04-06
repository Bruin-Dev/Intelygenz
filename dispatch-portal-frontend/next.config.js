const withSass = require('@zeit/next-sass');
const {
  PHASE_DEVELOPMENT_SERVER,
  PHASE_PRODUCTION_BUILD
} = require('next/constants');

module.exports = phase => {
  // when started in development mode `next dev` or `npm run dev` regardless of the value of STAGING environmental variable
  const isDev = phase === PHASE_DEVELOPMENT_SERVER;
  // when `next build` or `npm run build` is used, todo: but then use npm start
  const isProd =
    phase !== PHASE_DEVELOPMENT_SERVER && process.env.NODE_ENV === 'production';
  // when `next build` or `npm run build` is used
  /* const isStaging =
    phase === PHASE_PRODUCTION_BUILD && process.env.NODE_ENV !== 'production';
  */
  console.log(`isDev:${isDev}  isProd:${isProd}`);

  const MOCKS_SERVICES = {
    LOGIN: 'LOGIN',
    GET_DISPATCH: 'GET_DISPATCH',
    CREATE_DISPATCH: 'CREATE_DISPATCH',
    GET_ALL_DISPATCHES: 'GET_ALL_DISPATCHES'
  };

  const env = {
    BASE_API: (() => {
      if (isDev) return 'http://127.0.0.1:5004';
      if (isProd) return 'https://google.com/';
      return 'BASE_API:not SET';
    })(),
    BASE_PATH: (() => {
      if (isDev) return '/';
      if (isProd) return '/dispatch_portal/';
      return 'BASE_PATH:not SET';
    })(),
    ACTIVATED_MOCKS: (() => {
      if (isDev)
        return [MOCKS_SERVICES.LOGIN, MOCKS_SERVICES.GET_ALL_DISPATCHES];
      if (isProd)
        return [MOCKS_SERVICES.LOGIN, MOCKS_SERVICES.GET_ALL_DISPATCHES];
      return 'MOCKS:not SET';
    })(),
    MOCKS_SERVICES
  };

  return withSass({
    /* config options here */
    assetPrefix: env.BASE_PATH,
    env
  });
};
