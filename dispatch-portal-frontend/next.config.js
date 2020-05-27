const withSass = require('@zeit/next-sass');
const tailwindCss = require('tailwindcss');

const ENVIRONMENTS = {
  DEV: 'DEV',
  TEST: 'TEST',
  PRO: 'PRO'
};

const currentEnv = process.env.CURRENT_ENV || ENVIRONMENTS.DEV;

console.log(currentEnv);

const env = (() => {
  switch (currentEnv) {
    case ENVIRONMENTS.DEV || ENVIRONMENTS.TEST:
      return {
        BASE_API: 'http://127.0.0.1:8080/dispatch_portal/api',
        BASE_PATH: '/'
      };
    case ENVIRONMENTS.PRO:
      return {
        BASE_API: `${process.env.DNS_ENVIRONMENT}/dispatch_portal/api`,
        BASE_PATH: '/dispatch_portal/'
      };
    default:
      return {
        BASE_API: 'BASE_API:not SET',
        BASE_PATH: 'BASE_PATH:not SET'
      };
  }
})();

console.log(env);

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
