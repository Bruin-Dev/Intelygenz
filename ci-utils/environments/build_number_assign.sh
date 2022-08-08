#!/bin/bash

# Read the result of obtaining latest images for all modules
function get_latest_docker_images() {
  LATEST_IMAGES_FOR_ECR_REPOSITORIES=$(cat /tmp/latest_images_for_ecr_repositories.json)
}

# Use JSON result to create dynamically variables for the latest docker image of each repository
function declare_variables_for_latest_docker_images() {
  for repository in $(jq -r '.[] | .repository' <<< "${LATEST_IMAGES_FOR_ECR_REPOSITORIES}"); do
      MODULE_NAME="${repository}"
      MODULE_NAME_VARIABLE="$(printf '%s\n' "${MODULE_NAME//-/_}" | awk '{ print toupper($0) }')_BUILD_NUMBER"
      MODULE_LATEST_BUILD_NUMBER=$(jq --arg MODULE_NAME "$MODULE_NAME" -r '.[] | select(.repository == $MODULE_NAME) | .image_tag' <<< "${LATEST_IMAGES_FOR_ECR_REPOSITORIES}")
      export "${MODULE_NAME_VARIABLE}"="${MODULE_LATEST_BUILD_NUMBER}"
  done
}

function main() {
  get_latest_docker_images
  declare_variables_for_latest_docker_images
}

main