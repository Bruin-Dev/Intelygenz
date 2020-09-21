config:
  smtp:
    enabled: true
    sender: ${SMTP_USER_EMAIL}
    senderName: kre
    user: ${AWS_USERNAME_SES_KRE}
    pass: ${AWS_SES_KRE_SMTP_PASSWORD}
    host: ${SMTP_HOST_URL_KRE}
    port: ${SMTP_PORT_KRE}
  baseDomainName: ${BASE_DOMAIN_URL}
  admin:
    apiHost: api.${BASE_DOMAIN_URL}
    frontendBaseURL: https://admin.${BASE_DOMAIN_URL}
    # IMPORTANT: userEmail is used as the system admin user.
    # Use this for first login and create new users.
    userEmail: ${SMTP_USER_EMAIL}
  runtime:
    sharedStorageClass: hostpath
    # Uncomment this if you use a big dataset
    sharedStorageSize: 10Gi
    nats_streaming:
      storage:
        className: gp2
        # Uncomment this if your solution will receive a very large number of requests
        # size: 2Gi
    mongodb:
      persistentVolume:
        enabled: true
        storageClass: gp2
        # Uncomment this if you need more space for mongoDB
        # size: 5Gi
    chronograf:
      persistentVolume:
        enabled: true
        storageClass: gp2
    influxdb:
      persistentVolume:
        enabled: true
        storageClass: gp2
        # Uncomment this if you need more space for metrics and measurements on InfluxDB
        # size: 10Gi
  auth:
    jwtSignSecret: "${JWT_SIGN_SECRET_KRE}"
    secureCookie: true
    cookieDomain: ${BASE_DOMAIN_URL}

adminApi:
  tls:
    enabled: true
  host: api.${BASE_DOMAIN_URL}
  storage:
    class: hostpath

adminUI:
  tls:
    enabled: true
  host: admin.${BASE_DOMAIN_URL}

mongodb:
  mongodbDatabase: "${MONGODB_DATABASE}"
  mongodbUsername: "${MONGODB_USERNAME}"
  mongodbPassword: "${MONGODB_PASSWORD}"
  rootCredentials:
    username: "${MONGODB_ROOT_CRED_USERNAME}"
    password: "${MONGODB_ROOT_CRED_PASSWORD}"
  storage:
    className: gp2

certManager:
  enabled: true
  acme:
    # By default KRE use production letsencrypt url,
    # if you need a staging environment, uncomment this.
    # server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: ${SMTP_USER_EMAIL}
  dns01:
    route53:
      region: "${AWS_REGION}"
      hostedZoneID: "${HOSTED_ZONE_ID}"
      accessKeyID: "${AWS_ACCESS_KEY_ID}"
      secretAccessKey: "${AWS_SECRET_ACCESS_KEY}"