#!/bin/bash

repository=$1
image_tag=$(cat /tmp/latest_images_for_ecr_repositories.json | jq --arg repository_name ${repository} -r '.[] | select(.repository==$repository_name) | .image_tag')
echo -n "{\"image_tag\":\"${image_tag}\"}"