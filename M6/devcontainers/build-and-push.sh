#!/bin/bash
set -e

REGISTRY="localhost:5001"
IMAGE_NAME="wms-api"
TAG="${1:-latest}"

echo "Buduję obraz ${REGISTRY}/${IMAGE_NAME}:${TAG}..."
docker build -t "${REGISTRY}/${IMAGE_NAME}:${TAG}" ./wms-api

echo "Pushuję obraz do rejestru..."
docker push "${REGISTRY}/${IMAGE_NAME}:${TAG}"

echo "Obraz ${REGISTRY}/${IMAGE_NAME}:${TAG} został zbudowany i wypchnięty do rejestru."
