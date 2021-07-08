apiVersion: apps/v1
kind: Deployment
metadata:
  name: chronograf-proxy
  namespace: ${KRE_RUNTIME_NAME}
  labels:
    app: chronograf-proxy
spec:
  selector:
    matchLabels:
      app: chronograf-proxy
  template:
    metadata:
      labels:
        app: chronograf-proxy
    spec:
      containers:
        - name: nginx
          image: foxylion/nginx-self-signed-https
          ports:
            - containerPort: 80
          volumeMounts:
            - name: config
              mountPath: /etc/nginx/nginx.conf
              subPath: nginx.conf
            - name: config
              mountPath: /www/data/index.html
              subPath: index.html
            - name: config
              mountPath: /etc/apache2/.htpasswd
              subPath: .htpasswd
      volumes:
        - name: config
          configMap:
            name: chronograf-proxy-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: chronograf-proxy-config
  namespace: ${KRE_RUNTIME_NAME}
  labels:
    app: chronograf-proxy
data:
  nginx.conf: |
    user  nginx;
    worker_processes  1;
    error_log  /var/log/nginx/error.log warn;
    pid        /var/run/nginx.pid;
    events {
        worker_connections  1024;
    }
    http {
      include       /etc/nginx/mime.types;
      default_type  application/octet-stream;
      log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                          '$status $body_bytes_sent "$http_referer" '
                          '"$http_user_agent" "$http_x_forwarded_for"';
      access_log  /var/log/nginx/access.log  main;
      sendfile        on;
      keepalive_timeout  65;

      server {
        listen 80;
        resolver kube-dns.kube-system.svc.cluster.local valid=5s;
        root /www/data;
        auth_basic           "Admin Area";
        auth_basic_user_file /etc/apache2/.htpasswd;


        location ~ ^/dashboard$ { 
            return 301 https://$host/measurements/${KRE_RUNTIME_NAME}/sources/${KRE_RUNTIME_INFLUX_SOURCE}/dashboards/${KRE_RUNTIME_DASHBOARD}; 
        }
        location ~ ^/measurements/${KRE_RUNTIME_NAME}/(.*)$ {
            proxy_pass http://chronograf.${KRE_RUNTIME_NAME}.svc.cluster.local/measurements/${KRE_RUNTIME_NAME}/$1$is_args$args;
        }
      }
    }

  index.html: |
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Dashboard</title>
    </head>
    <body>
      <iframe
        src="/dashboard"
        frameborder="0" allowfullscreen
        style="position:absolute;top:0;left:0;width:100%;height:100%;"
      ></iframe>
    </body>
    </html>

  .htpasswd: |
        ${KRE_RUNTIME_DASHBOARD_USER}:${KRE_RUNTIME_DASHBOARD_PASSWORD}
---
apiVersion: v1
kind: Service
metadata:
  name: chronograf-proxy
  namespace: ${KRE_RUNTIME_NAME}
  labels:
    app: chronograf-proxy
spec:
  clusterIP: None
  ports:
  - name: web
    port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: chronograf-proxy
  sessionAffinity: None
  type: ClusterIP
status:
---
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    cert-manager.io/cluster-issuer: ${KRE_RUNTIME_NAME}-clusterissuer-runtimes-entrypoints
    kubernetes.io/ingress.class: nginx
    kubernetes.io/tls-acme: "true"
    nginx.ingress.kubernetes.io/default-backend: chronograf-proxy
  labels:
    app: chronograf-proxy
  name: chronograf-proxy
  namespace: ${KRE_RUNTIME_NAME}
spec:
  rules:
  - host: monitor.${KRE_RUNTIME_NAME}.mettel-automation.net
    http:
      paths:
      - backend:
          serviceName: chronograf-proxy
          servicePort: web
        path: /
        pathType: ImplementationSpecific
  tls:
  - hosts:
    - monitor.${KRE_RUNTIME_NAME}.mettel-automation.net
    secretName: monitor.${KRE_RUNTIME_NAME}.mettel-automation.net-tls
