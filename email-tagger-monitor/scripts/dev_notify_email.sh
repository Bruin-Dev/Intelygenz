#!/bin/sh


JSON_FILE=$1

# public alias
export HASH="email-tagger-dev"
# export HASH="ff086d74"

# export REQUEST_API_KEY="vcY5L1lfsQEHcUolkd928FU2tAU2aB2NCmutMlV77bA="
export REQUEST_API_KEY=""
export SIGNATURE_SECRET_KEY="dev-shared-secret-body-signature"
export EMAIL_WEBHOOK_URL="https://${HASH}.mettel-automation.net/api/email-tagger-webhook/email"

PAYLOAD=$(cat $JSON_FILE | python scripts/randomize.py)
SIGNATURE=$(echo $PAYLOAD | python scripts/signature.py)

# Uncomment to enable API KEY header
# API_KEY_HEADER="-H \"api-key: ${REQUEST_API_KEY}\""
API_KEY_HEADER=""

echo "PAYLOAD: ${PAYLOAD}"
echo "SIGNATURE: ${SIGNATURE}"

curl -i -XPOST \
  -H 'content-type: application/json' \
  $API_KEY_HEADER \
  -H "x-bruin-webhook-signature: ${SIGNATURE}" \
  --data "${PAYLOAD}"  ${EMAIL_WEBHOOK_URL}

