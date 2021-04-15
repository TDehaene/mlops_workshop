#!/bin/bash
CLUSTERNAME=bricsys-kubeflow-mlops
PROJECT=third-being-310214
ZONE=europe-west1-b

gcloud config set compute/zone $ZONE
gcloud container clusters create $CLUSTERNAME \
  --project $PROJECT \
  --cluster-version 1.17.17-gke.2800 \
  --scopes "https://www.googleapis.com/auth/cloud-platform" \
  --enable-stackdriver-kubernetes \
  --no-enable-legacy-authorization \
  --enable-master-authorized-networks \
  --no-enable-autorepair \
  --no-enable-autoupgrade \
  --no-enable-basic-auth \
  --enable-network-policy \
  --network third-being-310214-vpc \
  --create-subnetwork name=bricsys-kubeflow-subnet \
  --enable-ip-alias \
  --enable-private-nodes \
  --master-ipv4-cidr 172.16.0.32/28 \
  --enable-master-authorized-networks \
  --master-authorized-networks 178.116.225.72/32 \
  --zone $ZONE \
  --machine-type n1-standard-4 \
  --num-nodes 3

echo "cluster created"

kubectl create clusterrolebinding ml-pipeline-admin-binding --clusterrole=cluster-admin --user=$(gcloud config get-value account)

echo "clusterrole created"

# https://github.com/kubeflow/pipelines/tree/master/manifests/kustomize
PIPELINE_VERSION=0.5.1
kubectl apply -k github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=$PIPELINE_VERSION
echo "kubeflow pipeline deployment created"