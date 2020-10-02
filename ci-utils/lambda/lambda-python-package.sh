#!/bin/bash
LAMBDA_DIR=$1
LAMBDA_NAME=$2
LAMBDA_MAIN_NAME=$3

INITIAL_DIR=$(pwd)

cd "${LAMBDA_DIR}" || exit 1
echo "Installing dependencies from directory ${LAMBDA_DIR}"
pip3 install --target ./package -r requirements.txt --use-feature=2020-resolver
cd package || exit 1
echo "Zipping dependencies in directory ${LAMBDA_DIR}package"
zip -r9 "${OLDPWD}"/"${LAMBDA_NAME}".zip .
cd "$OLDPWD" || exit 1
echo "Zipping code in ${LAMBDA_DIR}${LAMBDA_NAME}.zip"
zip -g "${LAMBDA_NAME}".zip "${LAMBDA_MAIN_NAME}"

echo "Lambda code and dependencies zipped successfully in ${LAMBDA_DIR}${LAMBDA_NAME}.zip"

cd "$INITIAL_DIR" || exit 1