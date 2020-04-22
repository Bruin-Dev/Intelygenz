FROM node:10

# Setting working directory. All the path will be relative to WORKDIR
WORKDIR /usr/src/app

# Installing dependencies
COPY package*.json ./
RUN npm install

# Copying source files
COPY . .

# Building app
RUN npm run build

# Expose the listening port
EXPOSE 3000

# Run container as non-root (unprivileged) user
# The node user is provided in the Node.js base image
USER node

HEALTHCHECK --timeout=30s --interval=1m30s --retries=5 \
  CMD curl -s --fail http://localhost:3000 || exit 1

# Running the app
CMD [ "npm", "start" ]