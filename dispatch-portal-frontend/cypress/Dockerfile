# This Docker file is for building this project on Codeship Pro
# https://documentation.codeship.com/pro/languages-frameworks/nodejs/

# use Cypress provided image with all dependencies included
FROM cypress/base:10
WORKDIR /home/node/app

# Installing dependencies
COPY dispatch-portal-frontend/package*.json ./
# should be ci(package-lock)
RUN npm install

# Copying source files
COPY dispatch-portal-frontend/ .

# avoid many lines of progress bars during install
# https://github.com/cypress-io/cypress/issues/1243
ENV CI=1

# check if the binary was installed successfully
RUN $(npm bin)/cypress verify

# Building app
RUN npm run build

# Running the app
CMD [ "npm", "run", "ci:test" ]
