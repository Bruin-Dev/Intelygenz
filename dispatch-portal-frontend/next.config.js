const withSass = require('@zeit/next-sass');
const tailwindCss = require('tailwindcss');

const ENVIRONMENTS = {
  LOCAL: 'LOCAL',
  TEST_E2E: 'TEST_E2E',
  PRO: 'PRO'
};

const currentEnv = process.env.CURRENT_ENV || ENVIRONMENTS.LOCAL; // default dev, for local development

const env = (() => {
  switch (currentEnv) {
    case ENVIRONMENTS.LOCAL:
      return {
        BASE_API: 'http://127.0.0.1:8080/dispatch_portal/api',
        BASE_PATH: '/',
        ENVIRONMENT: ENVIRONMENTS.LOCAL,
        MOCKS: true
      };
    case ENVIRONMENTS.TEST_E2E:
      return {
        BASE_API: '/dispatch_portal/api',
        BASE_PATH: '/dispatch_portal/',
        ENVIRONMENT: ENVIRONMENTS.TEST_E2E,
        MOCKS: true
      };
    case ENVIRONMENTS.PRO:
      return {
        BASE_API: `${process.env.DNS_ENVIRONMENT}/dispatch_portal/api`,
        BASE_PATH: '/dispatch_portal/',
        ENVIRONMENT: ENVIRONMENTS.PRO,
        MOCKS: false
      };
    default:
      return {
        BASE_API: 'BASE_API:not SET',
        BASE_PATH: 'BASE_PATH:not SET',
        ENVIRONMENT: 'ENVIRONMENT:not SET',
        MOCKS: 'MOCKS:not SET'
      };
  }
})();

module.exports = withSass({
  webpack(config) {
    const rules = [
      {
        test: /\.scss$/,
        use: [
          {
            loader: 'postcss-loader',
            options: {
              ident: 'postcss',
              plugins: [tailwindCss('./tailwind.config.js')]
            }
          },
          { loader: 'sass-loader' }
        ]
      },
      {
        test: /\.(png|jpg|gif|svg|eot|ttf|woff|woff2)$/,
        use: {
          loader: 'url-loader',
          options: {
            limit: 100000
          }
        }
      }
    ];

    return {
      ...config,
      module: {
        ...config.module,
        rules: [...config.module.rules, ...rules]
      }
    };
  },
  /* config options here */
  assetPrefix: env.BASE_PATH,
  env
});
