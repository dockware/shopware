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

# CircleCI needs to know which git ref to build.
# without it, CircleCI always builds the default branch (main), which would install
# the Shopware version of main, even if the release was started on a LTS branch.
# git tags (e.g. sw-6.7.9.1) need to be sent as "tag", everything else is a branch
case "$BRANCH" in
  sw-*|essentials-*) REF_TYPE="tag" ;;
  *)                 REF_TYPE="branch" ;;
esac

cat <<EOT > body.json
{
  "$REF_TYPE": "$BRANCH",
  "parameters": {
    "imageName": "$IMAGE_NAME",
    "imageTag": "$IMAGE_TAG",
    "setLatest": $IS_LATEST,
    "setMajorLatest": $IS_MAJOR_LATEST
  }
}
EOT

cat body.json

# fail the GitHub action, if CircleCI rejects the pipeline (e.g. unknown branch)
curl --fail-with-body -X POST -d @body.json \
     -H "Content-Type: application/json" \
     -H "Circle-Token: $TOKEN" \
     "https://circleci.com/api/v2/project/github/dockware/$REPO_NAME/pipeline"
RESULT=$?

rm -rf body.json

exit $RESULT