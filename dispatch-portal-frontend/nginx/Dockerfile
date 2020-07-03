# Base on offical NGINX Alpine image
FROM nginx:1.19.0-alpine

# Remove any existing config files
RUN rm /etc/nginx/conf.d/*

# Copy custom entrypoint
COPY dispatch-portal-frontend/nginx/nginx-entrypoint.sh /
RUN chmod +x /nginx-entrypoint.sh

# Copy config files
COPY dispatch-portal-frontend/nginx/nginx.conf.template /etc/nginx/conf.d/nginx.conf.template

RUN apk update && apk add bash curl

# Expose the listening port
EXPOSE 8080

# Launch NGINX
ENTRYPOINT ["/nginx-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]