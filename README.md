# Data Collector

# Overview 
 This script is an example data collection engine that collects resources from a source API. A resource is defined as an individual record retrieved from the Source API.
 Once the resource is successfully called, it then sends the resource to the Processing API. Furthermore, Once a successful 201 response is recieved, it is then send to the Storage API.
 This script supports concurrent data collection using workers. This script was deployed using the following tools/versions
 Tested on the following setup: docker (24.0.4), minikube (v1.31.2), kubecli (v1.27.2), helm (v3.12.3)
 requirements.txt includes aiohttp (https://pypi.org/project/aiohttp/)

# Pre-requisites 
* Python 3.8 or higher (Docker uses 3.9)
* Docker with Kubernetes 
* Helm Deployment over Pod (Service type: NodePort)

# How to Configure
 Customize values within mychart/templates/values.yaml
## List of configurable values below: 
* numResourceWorkers
* apiEndpoint
* xAuthToken
* resourceIdStart
* resourceIdEnd
* secondApiEndpoint
* secondApiAuthToken
* thirdApiEndpoint
* thirdApiAuthToken

> Requires valid endpoints to be configured before moving forward.

# How to deploy and run 
* Alias: kubectl = k

 deploy docker desktop 
1. Run minikube 
``` minikube start ```
2. check minikube status confirm 
``` minikube status```
3. helm install or upgrade (if revised)
``` helm install data-collector-app myChart/ --values myChart/values.yaml ```
``` helm upgrade data-collector-app myChart --set deployment.tag=1.0.1 ```
4. confirm list of all applications (app name: data-collector-app)
``` helm list ``` 
5. Use the echo command and run using the IP port from step 5. 
  ``` echo http://$NODE_IP:$NODE_PORT ```
6. Confirm correct container for all pods:
``` k get deployments -o wide ```
7. Verify pods with names to use for individual log validation:
``` k get pods ```
8. To view logs on terminal/powershell or view individual based on pod name (step 7): 
``` k logs -f -l app=data-collector-app```
``` k logs data-collector-app-###### ```

# Known Issues / Concerns 
### Within the script, attempting to make use of semaphore. Have not fully tested if threads on the semaphore does their work correctly. 
### Assuming all sources have unique APIs and/or tokens. 
### Clarification needed regarding each pod/worker tasks. After further research I assume the best method was to use redis to have the pods communicate and share tasks, where worker_num 1 (pod 1) only focuses on retries. Did not have time to fully implement this. 

# Personal Notes:
## Using minikube for testing
* Alias: kubectl = k
 - start minikube:
``` minikube start ```
 - create deployment: 
``` k create deployment app-node --image=k8s.gcr.io/echoserver:1.4 ```
 - create service for load balancer in default namespace:
``` k expose deployment app-node --type=LoadBalancer --port=8000 -n default ```
 - using dev namespace, details on all events: 
``` k get events -n dev ```
 - apply yaml file from app directory:
``` k apply -f v1.yaml ```
 - confirm deployment:
``` k get deployment ```
 - list of all logs in kubectl:
``` k logs -f -l app=data-collector-app ```

## Helpful links: 
https://kubernetes.io/docs/reference/kubectl/cheatsheet/