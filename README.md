# MiniHub

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Build Status](https://travis-ci.org/matkovskim/uks-project.svg?branch=master)](https://travis-ci.org/matkovskim/uks-project)

## Description

MiniHub is a web application for managing projects which supports user collaboration on projects, creating and tracking issues, tracking changes in git repositories.

MiniHub is created for the purpose of the Software Configuration Management course at the Faculty of Technical Sciences, University of Novi sad.

## Deployment

MiniHub is deployed on Microsoft Azure cloud using the Azure Kubernetes Service and can be accessed [here](https://www.google.com).

## Instructions to run locally

1. Install **minikube** by following the [instructions](https://minikube.sigs.k8s.io/docs/start/)
2. Install **kubectl** by following the [instructions](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
3. Clone this repository to your local machine
4. Start minikube
```
$ minikube start
```
5. Give execute permission to the starting script (assuming you are positioned in the directory of the cloned repository)
```
$ chmod +x /kubernetes_config/start_script.sh
```
6. Run the starting script
```
$ ./kubernetes_config/start_script.sh
```
7. Open the application in browser
```
$ minikube service django-service
```

## Technologies used

- Django web framework for the application
- PostgreSQL database
- Redis for caching
- Filebeat + Elasticsearch + Kibana for processing, storing and visualizing logs
- Prometheus + Grafana for monitoring and visualization of monitoring data
- Docker for containerization
- Kubernetes (Azure Kubernetes Service) for deployment, scaling and management of containerized applications
- Travis CI for running tests and building

## Contributors

- [Marijana Matkovski](https://github.com/matkovskim)  
- [Marijana Kološnjaji](https://github.com/majak96)  
- [Vesna Milić](https://github.com/vesnamilic)  
- [Miloš Krstić](https://github.com/KrsticM)  
- [Jelena Šurlan](https://github.com/jaseyrae9)  
