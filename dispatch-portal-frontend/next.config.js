const withSass = require('@zeit/next-sass');
const tailwindCss = require('tailwindcss');

const isDev = process.env.NODE_ENV !== 'production';
const isProd = process.env.NODE_ENV === 'production';

const env = {
  BASE_API: (() => {
    if (isDev) return 'http://127.0.0.1:8080/dispatch_portal/api';
    if (isProd) return `${process.env.DNS_ENVIRONMENT}/dispatch_portal/api`;
    return 'BASE_API:not SET';
  })(),
  BASE_PATH: (() => {
    if (isDev) return '/';
    if (isProd) return '/dispatch_portal/';
    return 'BASE_PATH:not SET';
  })()
};

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
