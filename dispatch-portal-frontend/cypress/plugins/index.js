// eslint-disable-next-line global-require,import/no-extraneous-dependencies
const cucumber = require('cypress-cucumber-preprocessor').default;

module.exports = (on, config) => {
  on('file:preprocessor', cucumber());
};
