# Data Collector

# Overview 
 This script is an example data collection engine that collects resources from a source API. A resource is defined as an individual record retrieved from the Source API.
 Once the resource is successfully called, it then sends the resource to the Processing API. Furthermore, Once a successful 201 response is recieved, it is then send to the Storage API.
 This script supports concurrent data collection using workers. This script was deployed using the following tools/versions
 Tested on the following setup: minikube (v1.31.2), kubecli (v1.27.2), helm (v3.12.3)
 requirements.txt includes aiohttp (https://pypi.org/project/aiohttp/)

# Pre-requisites 
* Python 3.8 or higher (Docker uses 3.9)
* Docker with Kubernetes 
* Helm Deployment over Pod

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
 deploy docker desktop 
1. Run minikube 
``` minikube start ```
2. check minikube status confirm 
``` check minikube dashboard --url```
3. apply v1.yaml file 
``` kubectl apply -f v1.yaml```
4. verify pods
``` kubectl get pods ```
5. when testing locally, expose port: 
``` kubectl expose deployment retry-node --type=LoadBalancer --port=8000 -n dev```
6. to view logs on seperate terminal/powershell: 
``` kubectl logs -f -l app=data-collector```

# Known Issues / Concerns 
# Within the script, attempting to make use of semaphore. Have not fully tested if threads on the semaphore does their work correctly.

# Assuming all three APIs systems will require unique tokens. I should have asked for more clarification on this. 

# Minikube notes
* Alias: kubectl = k

## Using minikube for testing
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
``` k logs -f -l app=data-collector ```


## local testing from root directory run: 
``` curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256" ```
 start service: 
``` minikube service app-name ```
