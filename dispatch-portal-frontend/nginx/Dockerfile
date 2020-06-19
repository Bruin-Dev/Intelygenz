# Base on offical NGINX Alpine image
FROM nginx:1.19.0-alpine

# Remove any existing config files
RUN rm /etc/nginx/conf.d/*

# Copy config files
COPY dispatch-portal-frontend/nginx/nginx.conf /etc/nginx/nginx.conf

RUN apk update && apk add bash curl

# Expose the listening port
EXPOSE 8080

# Launch NGINX
#CMD [ "nginx", "-g", "daemon off;" ]