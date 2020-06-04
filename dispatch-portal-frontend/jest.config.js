module.exports = {
  collectCoverageFrom: ['**/*.{js,jsx,ts,tsx}'],
  coveragePathIgnorePatterns: ['/__mocks__/'],
  coverageReporters: ['clover', 'json', 'json-summary', 'lcov', 'text'],
  coverageThreshold: {
    global: {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    }
  },
  modulePathIgnorePatterns: [
    '<rootDir>/.next/',
    '<rootDir>/.storybook/',
    '<rootDir>/node_modules/',
    '<rootDir>/coverage/',
    '<rootDir>/cypress/',
    '<rootDir>/nginx/',
    '<rootDir>/public/',
    '<rootDir>/build/',
    '<rootDir>/out/',
    '<rootDir>/tmp-*/',
    '<rootDir>/babel.config.js',
    '<rootDir>/jest.config.js',
    '<rootDir>/next.config.js',
    '<rootDir>/tailwind.config.js'
  ],
  transform: {
    '^.+\\.[t|j]sx?$': 'babel-jest'
  },
  moduleNameMapper: {
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$':
      '<rootDir>/__mocks__/fileMock.js', // Todo: review this line
    '\\.(css|scss)$': 'identity-obj-proxy'
  }
};
