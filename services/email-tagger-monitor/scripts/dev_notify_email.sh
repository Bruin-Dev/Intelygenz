#!/bin/sh

JSON_FILE=$1

if [ $# -eq 0 ]
  then
    echo "No json file supplied"
    echo "Example:"
    echo "> ./local_notify_email.sh test_email.json"
    exit 1
fi


export SIGNATURE_SECRET_KEY="dev-shared-secret-body-signature"
export EMAIL_WEBHOOK_URL="http://localhost:5055/api/email-tagger-webhook/email"

PAYLOAD=$(cat $JSON_FILE | python scripts/randomize.py)
SIGNATURE=$(echo $PAYLOAD | python scripts/signature.py)

echo "PAYLOAD: ${PAYLOAD}"
echo "SIGNATURE: ${SIGNATURE}"

curl -i -XPOST \
  -H 'content-type: application/json' \
  -H "x-bruin-webhook-signature: ${SIGNATURE}" \
  --data "${PAYLOAD}"  ${EMAIL_WEBHOOK_URL}
