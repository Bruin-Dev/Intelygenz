#!/bin/sh


JSON_FILE=$1

# export REQUEST_API_KEY="vcY5L1lfsQEHcUolkd928FU2tAU2aB2NCmutMlV77bA="
export REQUEST_API_KEY=""
export SIGNATURE_SECRET_KEY="hxCr1/RWNOaHEKvX9FY05ocQq9f0VjTmhxCr1/RWNOZw4U4x5nXsFA=="
export EMAIL_WEBHOOK_URL="http://localhost:5055/api/email-tagger-webhook/ticket"

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
