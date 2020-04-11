#!/bin/bash

echo "Postgres database:"
kubectl create -f postgres-credentials.yaml
kubectl create -f postgres-volume.yaml
kubectl create -f postgres-volume-claim.yaml
kubectl create -f postgres-deployment.yaml

echo "Redis:"
kubectl create -f redis-deployment.yaml

echo "Django:"
kubectl create -f secret-key-credentials.yaml
kubectl create -f mail-credentials.yaml
kubectl create -f media-volume.yaml
kubectl create -f media-volume-claim.yaml
kubectl create -f django-deployment.yaml

echo "Elasticsearch:"
kubectl create -f elasticsearch-config.yaml
kubectl create -f elasticsearch-volume.yaml
kubectl create -f elasticsearch-volume-claim.yaml
kubectl create -f elasticsearch-deployment.yaml

echo "Filebeat:"
kubectl create -f filebeat-indices-configmap.yaml
kubectl create -f filebeat-settings-configmap.yaml
kubectl create -f filebeat-daemonset.yaml
kubectl create -f filebeat-permissions.yaml

echo "Kibana:"
kubectl create -f kibana-deployment.yaml
