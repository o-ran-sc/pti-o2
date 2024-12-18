## Building containers

To accommodate the git repo access issue, the cgts-client and distributed client are
cloned into temp before docker building

```sh
mkdir -p temp
cd temp
git clone --branch r/stx.9.0 https://opendev.org/starlingx/config.git
git clone --branch r/stx.9.0 https://opendev.org/starlingx/distcloud-client.git
git clone --branch r/stx.9.0 https://opendev.org/starlingx/fault.git
cd distcloud-client
patch -p1 < ../../patches/stx-distcloud-client/distclient-insecure.patch
cd -
```

```sh
docker-compose build
```

## Running the tests


```sh
source ./admin_openrc.sh
export |grep OS_AUTH_URL
export |grep OS_USERNAME
export |grep OS_PASSWORD
docker-compose up -d
docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration
```

## Running the tests with a O-Cloud

Prerequisite: in case of testing against real ocloud, download openrc file from ocloud dashboard, e.g. 

```sh
admin_openrc.sh
docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration-ocloud

docker-compose run --rm --no-deps --entrypoint=pytest api /tests/integration-ocloud --log-level=DEBUG --log-file=/test
s/debug.log
```

## Tear down containers

```sh
docker-compose down --remove-orphans
```

## Test with local virtualenv

```sh
python3.8 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -c constraints.txt
pip install -r requirements-test.txt
pip install -e o2ims
# pip install -e o2dms -e o2common
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```


Test O2DMS with docker-compose
==============================

## setup account over INF and get token

```sh
USER="admin-user"
NAMESPACE="kube-system"

cat <<EOF > admin-login.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ${USER}
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ${USER}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: ${USER}
  namespace: kube-system
EOF
kubectl apply -f admin-login.yaml
TOKEN_DATA=$(kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep ${USER} | awk '{print $1}') | grep "token:" | awk '{print $2}')

```

## setup remote cli to access kubenetes cluster over INF

```sh
sudo apt-get install -y apt-transport-https
echo "deb http://mirrors.ustc.edu.cn/kubernetes/apt kubernetes-xenial main" | \
sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl

source <(kubectl completion bash) # setup autocomplete in bash into the current shell, bash-completion package should be installed first.
echo "source <(kubectl completion bash)" >> ~/.bashrc # add autocomplete permanently to your bash shell.

https://get.helm.sh/helm-v3.5.3-linux-amd64.tar.gz
tar xvf helm-v3.5.3-linux-amd64.tar.gz
sudo cp linux-amd64/helm /usr/local/bin

source <(helm completion bash)
echo "source <(helm completion bash)" >> ~/.bashrc

OAM_IP=<INF OAM IP>
NAMESPACE=default
TOKEN_DATA=<TOKEN_DATA from INF>

USER="admin-user"

kubectl config set-cluster inf-cluster --server=https://${OAM_IP}:6443 --insecure-skip-tls-verify
kubectl config set-credentials ${USER} --token=$TOKEN_DATA
kubectl config  set-context ${USER}@inf-cluster --cluster=inf-cluster --user ${USER} --namespace=${NAMESPACE}
kubectl config use-context ${USER}@inf-cluster

kubectl get pods -A

```


## setup local repo: o2imsrepo

```sh
helm repo add chartmuseum https://chartmuseum.github.io/charts
helm repo update
helm pull chartmuseum/chartmuseum # download chartmuseum-3.4.0.tgz to local
tar zxvf chartmuseum-3.4.0.tgz

export NODE_IP=<INF OAM IP>

cat <<EOF>chartmuseum-override.yaml
env:
  open:
    DISABLE_API: false
service:
  type: NodePort
  nodePort: 30330
EOF

helm install chartmuseumrepo chartmuseum/chartmuseum -f chartmuseum-override.yaml
kubectl get pods
Kubectl get services

helm repo add o2imsrepo http://${NODE_IP}:30330
helm repo update

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm pull bitnami/mysql
helm push mysql-8.8.16.tgz o2imsrepo
helm repo update

helm install my-release o2imsrepo/mysql
kubectl get pods
helm del my-release

```



## Verify CFW over INF: Test with cnf firewall-host-netdevice

## Setup host netdevice over INF

```sh
ssh sysadmin@<inf oam IP>
sudo ip link add name veth11 type veth peer name veth12
sudo ip link add name veth21 type veth peer name veth22
sudo ip link |grep veth
exit
```


## verify CNF over INF
```sh
git clone https://github.com/biny993/firewall-host-netdevice.git

cat <<EOF> cfw-hostdev-override.yaml

image:
  repository: ubuntu
  tag: 18.04
  pullPolicy: IfNotPresent

resources:
  cpu: 2
  memory: 2Gi
  hugepage: 256Mi

#global vars for parent and subcharts.


  unprotectedNetPortVpg: veth11
  unprotectedNetPortVfw: veth12
  unprotectedNetCidr: 10.10.1.0/24
  unprotectedNetGwIp: 10.10.1.1

  protectedNetPortVfw: veth21
  protectedNetPortVsn: veth22
  protectedNetCidr: 10.10.2.0/24
  protectedNetGwIp: 10.10.2.1

  vfwPrivateIp0: 10.10.1.1
  vfwPrivateIp1: 10.10.2.1

  vpgPrivateIp0: 10.10.1.2

  vsnPrivateIp0: 10.10.2.2

EOF

helm install cfw1 firewall-host-netdevice -f cfw-hostdev-override.yaml
kubectl get pods
helm del cfw1
```

## push repo to o2imsrepo

```sh
tar -zcvf firewall-host-netdevice-1.0.0.tgz firewall-host-netdevice/
helm push firewall-host-netdevice-1.0.0.tgz o2imsrepo
helm repo update
helm search repo firewall

helm install cfw1 o2imsrepo/firewall-host-netdevice -f cfw-hostdev-override.yaml
kubectl get pods
helm del cfw1
```

## build docker image for o2 services
```sh
cd o2
docker-compose build

```

## bootstrap o2 service with docker-compose
```sh

mkdir -p temp/kubeconfig/
cp <your .kube/config> temp/kubeconfig/

source ./admin_openrc.sh
export K8S_KUBECONFIG=/etc/kubeconfig/config
docker-compose up -d
docker logs -f o2_redis_pubsub_1

```

## simiulate SMO to deploy CFW

```sh

curl --location --request GET 'http://localhost:5005/o2ims_infrastructureInventory/v1/deploymentManagers'
export dmsId=<DMS ID>
curl --location --request POST 'http://localhost:5005/o2dms/v1/${dmsId}/O2dms_DeploymentLifecycle/NfDeploymentDescriptor' \
--header 'Content-Type: application/json' \
--data-raw '{
  "name": "cfwdesc1",
  "description": "demo nf deployment descriptor",
  "artifactRepoUrl": "http://128.224.115.15:30330",
  "artifactName": "firewall-host-netdevice",
  "inputParams": 
  "{\n  \"image\": {\n    \"repository\": \"ubuntu\",\n    \"tag\": 18.04,\n    \"pullPolicy\": \"IfNotPresent\"\n  },\n  \"resources\": {\n    \"cpu\": 2,\n    \"memory\": \"2Gi\",\n    \"hugepage\": \"256Mi\",\n    \"unprotectedNetPortVpg\": \"veth11\",\n    \"unprotectedNetPortVfw\": \"veth12\",\n    \"unprotectedNetCidr\": \"10.10.1.0/24\",\n    \"unprotectedNetGwIp\": \"10.10.1.1\",\n    \"protectedNetPortVfw\": \"veth21\",\n    \"protectedNetPortVsn\": \"veth22\",\n    \"protectedNetCidr\": \"10.10.2.0/24\",\n    \"protectedNetGwIp\": \"10.10.2.1\",\n    \"vfwPrivateIp0\": \"10.10.1.1\",\n    \"vfwPrivateIp1\": \"10.10.2.1\",\n    \"vpgPrivateIp0\": \"10.10.1.2\",\n    \"vsnPrivateIp0\": \"10.10.2.2\"\n  }\n}",
  "outputParams": "{\"output1\": 100}"
}'

curl --location --request GET 'http://localhost:5005/o2dms/v1/${dmsId}/O2dms_DeploymentLifecycle/NfDeploymentDescriptor'

curl --location --request POST 'http://localhost:5005/o2dms/v1/${dmsId}/O2dms_DeploymentLifecycle/NfDeployment' \
--header 'Content-Type: application/json' \
--data-raw '{
  "name": "cfw100",
  "description": "demo nf deployment",
  "descriptorId": "<NfDeploymentDescriptorId>",
  "parentDeploymentId": ""
}'

curl --location --request GET 'http://localhost:5005/o2dms/v1/${dmsId}/O2dms_DeploymentLifecycle/NfDeployment'

export NfDeploymentId=<NfDeployment Id>

```

## check logs

```sh
docker logs -f o2_redis_pubsub_1
kubectl get pods
kubectl logs -f cfw100-sink-host-netdevice-59bf6fbd4b-845p4
```

## watch traffic stats

open browswer with url: http://<NODE_IP>:30667


## bring down CFW

```sh
curl --location --request DELETE 'http://localhost:5005/o2dms/v1/${dmsId}/O2dms_DeploymentLifecycle/NfDeployment/${NfDeploymentId}'
```
