#!/bin/bash

AKS_RESOURCE_GROUP=UKS
AKS_CLUSTER_NAME=UKSCluster
ACR_RESOURCE_GROUP=UKS
ACR_NAME=ftnukstim3

# Get the id of the service prinicpal configured for AKS
CLIENT_ID=$(az aks show --resource-group $AKS_RESOURCE_GROUP --name $AKS_CLUSTER_NAME --query "servicePrincipalProfile.clientId" --output tsv)
ACR_ID=$(az acr show --name $ACR_NAME --resource-group $ACR_RESOURCE_GROUP --query "id" --output tsv)

# Create role assignment
az role assignment create --assignee $CLIENT_ID --role acrpull --scope $ACR_ID