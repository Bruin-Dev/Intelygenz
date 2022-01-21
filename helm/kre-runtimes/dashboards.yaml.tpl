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

        location ~ ^/dashboard(.*)$ {
            return 302 https://$host/measurements/${KRE_RUNTIME_NAME}/sources/${KRE_RUNTIME_INFLUX_SOURCE}/dashboards/${KRE_RUNTIME_DASHBOARD}$1$args;
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
      <style>
        body{
            background-color: black;
            color: white;
            font-family: 'Roboto', Arial, Helvetica, sans-serif;
        }
        .filters_wrapper{}
        .filters{
            padding: 5px;
            border: 0px solid gray;
            height: 30px;
        }
        .predefined{}
        .predefined select{
            height: 24px;
        }
      </style>
      <title>Dashboard</title>
    </head>
    <body>
      <div class="filters_wrapper">
        <div class="predefined filters" style="float: right;">
            <select id="predefined_dates_filter" name="dates">
                <option value="now%28%29%20-%207d">default past 7d</option>
                <option value="now%28%29%20-%205m">past 5m</option>
                <option value="now%28%29%20-%2015m">past 15m</option>
                <option value="now%28%29%20-%201h">past 1h</option>
                <option value="now%28%29%20-%206h">past 6h</option>
                <option value="now%28%29%20-%2012h">past 12h</option>
                <option value="now%28%29%20-%2024h">past 24h</option>
                <option value="now%28%29%20-%202d">past 2d</option>
                <option value="now%28%29%20-%207d">past 7d</option>
                <option value="now%28%29%20-%2030d">past 30d</option>
                <!-- Custom predefined values -->
                this_week, last_week, current_month, last_month
                <option value="this_week">current week</option>
                <option value="last_week">last week</option>
                <option value="current_month">current month</option>
                <option value="last_month">last month</option>
            </select>
        </div>
        <h1>${KRE_RUNTIME_NAME} Dashboard</h1>
      </div>
      <iframe id="mettel_public_dashboard" width="100%" height="100%"
            src="/dashboard?lower=now%28%29%20-%207d"
            frameborder="0"
            style="position:absolute;top:60px;left:0;width:100%;height:100%;" allowfullscreen
      >
      </iframe>
      <script>
         const MONITOR_BASE_URL = "https://monitor.${KRE_RUNTIME_DASHBOARD_DNS}.mettel-automation.net/dashboard"

         function formatDate(d){
             return d.toISOString().split('T')[0];
         }

         function getCurrentWeek(){
             const curr = new Date;
             const first = curr.getDate() - curr.getDay(); // First day is the day of the month - the day of the week
             const last = first + 6; // last day is the first day + 6
             const firstday = formatDate(new Date(curr.setDate(first)))
             const lastday = formatDate(new Date(curr.setDate(last)))
             return {
                firstday, lastday
             }
         }

         function getLastWeek(){
             const curr = new Date;
             const first = curr.getDate() - curr.getDay(); // First day is the day of the month - the day of the week
             const firstLastWeek = curr.getDate() - curr.getDay() - 7; // First day is the day of the month - the day of the week
             const lastWeek = first + 6 - 7; // last day is the first day + 6
             const firstday = formatDate(new Date(curr.setDate(firstLastWeek)));
             const lastday = formatDate(new Date(curr.setDate(lastWeek)));
             return {
                firstday, lastday
             }
         }

         function getCurrentMonth(){
             const curr = new Date;
             const firstdayCurrMonth = new Date(curr.getFullYear(), curr.getMonth(), 2);
             const lastdayCurrMonth = new Date(curr.getFullYear(), curr.getMonth() + 1, 2);
             const firstday = formatDate(firstdayCurrMonth);
             const lastday = formatDate(lastdayCurrMonth);
             return {
                firstday, lastday
             }
         }

         function getPreviousMonth(){
             const curr = new Date;
             const prevMonthLastDate = new Date(curr.getFullYear(), curr.getMonth(), 2);
             const prevMonthFirstDate = new Date(curr.getFullYear() - (curr.getMonth() > 0 ? 0 : 1), (curr.getMonth() - 1 + 12) % 12, 2);
             const firstday = formatDate(prevMonthFirstDate);
             const lastday = formatDate(prevMonthLastDate);
             return {
                firstday, lastday
             }
         }

         document.addEventListener('DOMContentLoaded', function() {
             var predefinedValues = document.getElementById('predefined_dates_filter');
             predefinedValues.onchange = (event) => {
                 const inputText = event.target.value;

                 let monitor_url_with_filters = "";
                 switch (inputText) {
                    case "this_week":
                        const dates = getCurrentWeek()
                        monitor_url_with_filters = MONITOR_BASE_URL +
                            "?lower=" + dates.firstday + "&upper=" + dates.lastday;
                        break;
                    case "last_week":
                        const datesLastWeek = getLastWeek()
                        monitor_url_with_filters = MONITOR_BASE_URL +
                            "?lower=" + datesLastWeek.firstday + "&upper=" + datesLastWeek.lastday;
                        break;
                    case "current_month":
                        const datesCurrentMonth = getCurrentMonth()
                        monitor_url_with_filters = MONITOR_BASE_URL +
                            "?lower=" + datesCurrentMonth.firstday + "&upper=" + datesCurrentMonth.lastday;
                        break;
                    case "last_month":
                        const datesLastMonth = getPreviousMonth()
                        monitor_url_with_filters = MONITOR_BASE_URL +
                            "?lower=" + datesLastMonth.firstday + "&upper=" + datesLastMonth.lastday;
                        break;
                    default:
                        monitor_url_with_filters = MONITOR_BASE_URL + "?lower=" + inputText;
                        break;
                 }
                 if (monitor_url_with_filters !== "") {
                     document.getElementById("mettel_public_dashboard").src = monitor_url_with_filters;
                 }else{
                     console.log("Error: filters empty!")
                 }
             };
         }, false);
      </script>
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
  - host: monitor.${KRE_RUNTIME_DASHBOARD_DNS}.mettel-automation.net
    http:
      paths:
      - backend:
          serviceName: chronograf-proxy
          servicePort: web
        path: /
        pathType: ImplementationSpecific
  tls:
  - hosts:
    - monitor.${KRE_RUNTIME_DASHBOARD_DNS}.mettel-automation.net
    secretName: monitor.${KRE_RUNTIME_DASHBOARD_DNS}.mettel-automation.net-tls
