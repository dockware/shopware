#!/bin/bash

REPO_NAME="shopware"

if [ $# -lt 6 ]; then
  echo "Usage: $0 <BRANCH> <CIRCLE_CI_TOKEN> <IMAGE_NAME> <IMAGE_TAG> <IS_LATEST> <IS_MAJOR_LATEST>"
  exit 1
fi

BRANCH=$1
TOKEN=$2
IMAGE_NAME=$3
IMAGE_TAG=$4
IS_LATEST=$5
IS_MAJOR_LATEST=$6

cat <<EOT > body.json
{
  "parameters": {
    "imageName": "$IMAGE_NAME",
    "imageTag": "$IMAGE_TAG",
    "setLatest": $IS_LATEST,
    "setMajorLatest": $IS_MAJOR_LATEST
  }
}
EOT

cat body.json

curl -X POST -d @body.json \
     -H "Content-Type: application/json" \
     -H "Circle-Token: $TOKEN" \
     "https://circleci.com/api/v2/project/github/dockware/$REPO_NAME/pipeline"

rm -rf body.json