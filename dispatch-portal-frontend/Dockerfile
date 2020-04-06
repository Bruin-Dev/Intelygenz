FROM node:10

# Setting working directory. All the path will be relative to WORKDIR
WORKDIR /usr/src/app

# Installing dependencies
COPY dispatch-portal-frontend/package*.json ./
RUN npm install

# Copying source files
COPY dispatch-portal-frontend/ .

ARG NODE_ENV
ENV NODE_ENV=${NODE_ENV}
ARG BASE_API_URL
ENV BASE_API_URL=${BASE_API_URL}
ARG DISPATCH_BACKEND_PORTAL_PORT
ENV DISPATCH_BACKEND_PORTAL_PORT=${DISPATCH_BACKEND_PORTAL_PORT}

# Building app
RUN npm run build

# Expose the listening port
EXPOSE 3000


HEALTHCHECK --timeout=30s --interval=1m30s --retries=5 \
  CMD curl -s --fail http://localhost:3000 || exit 1

# Running the app
CMD [ "npm", "start" ]