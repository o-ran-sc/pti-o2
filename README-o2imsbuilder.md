
## Build and deploy O2 services over O-Cloud (INF)


## Bring up builder container from O-Cloud controller node


```sh
mkdir -p /home/sysadmin/share
sudo docker run -dt --privileged -v /home/sysadmin/share/:/home/sysadmin/share/ -v /var/run:/var/run --name o2imsbuilder centos:7
```

## Build O2 service images inside the builder container


```sh
sudo docker exec -it o2imsbuilder bash
```


```sh
curl -L https://get.daocloud.io/docker/compose/releases/download/1.25.4/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose -v

yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
yum makecache fast
yum install -y docker-ce
docker ps

yum install -y git

cd /home/sysadmin/share/
git clone "https://gerrit.o-ran-sc.org/r/pti/o2"
cd o2

mkdir -p temp
cd temp
git clone --depth 1 --branch master https://opendev.org/starlingx/config.git
git clone --depth 1 --branch master https://opendev.org/starlingx/distcloud-client.git
cd -

docker-compose build

exit

```

### Push O2 service images to local registry (with auth user admin)

```sh
sudo docker tag o2imsdms:latest registry.local:9001/o-ran-sc/pti-o2imsdms:2.0.0
sudo docker image push registry.local:9001/o-ran-sc/pti-o2imsdms:2.0.0

```

## Deploy O2 services with helm chart over O-Cloud controller node (with auth user admin)

```sh
export NAMESPACE=oran-o2
kubectl create ns ${NAMESPACE}

cd /home/sysadmin/
source /etc/platform/openrc
cat <<EOF>ocloud-override.yaml
imagePullSecrets:
  - default-registry-key

o2ims:
  serviceaccountname: admin-oran-o2
  images:
    tags:
      img_o2: registry.local:9001/o-ran-sc/pti-o2imsdms:2.0.0
      img_postgres: docker.io/library/postgres:9.6
      img_redis: docker.io/library/redis:alpine
    pullPolicy: IfNotPresent
  logginglevel: "DEBUG"

ocloud:
  OS_AUTH_URL: "${OS_AUTH_URL}"
  OS_USERNAME: "${OS_USERNAME}"
  OS_PASSWORD: "${OS_PASSWORD}"
EOF

sudo docker login registry.local:9001 -u ${OS_PROJECT_NAME} -p ${OS_PASSWORD}

kubectl -n ${NAMESPACE} create secret docker-registry ${OS_PROJECT_NAME}-${NAMESPACE}-registry-secret \
--docker-server=registry.local:9001 --docker-username=${OS_PROJECT_NAME} \
--docker-password=${OS_PASSWORD} --docker-email=noreply@windriver.com

cd /home/sysadmin/share/o2

helm install o2imstest charts/ -f /home/sysadmin/ocloud-override.yaml

kubectl -n ${NAMESPACE} get pods

```

### test api endpoint

```sh
curl -k http(s)://<Node IP>:30205
curl -k http(s)://<Node IP>:30205/o2ims_infrastructureInventory/v1
```


### Debug tips

```sh
kubectl -n ${NAMESPACE} logs -f o2api-<xxx> -c o2api
kubectl -n ${NAMESPACE} logs -f o2api-<xxx> -c postgres
kubectl -n ${NAMESPACE} logs -f o2api-<xxx> -c o2pubsub
kubectl -n ${NAMESPACE} logs -f o2api-<xxx> -c watcher


kubectl -n ${NAMESPACE} logs -f o2api-<xxx> -c o2api

kubectl -n ${NAMESPACE} exec -it o2api-<xxx> -c postgres -- bash
    psql -U o2ims

        \c o2ims

        \d

        select * from ocloud;

        \q

    exit

```

## Issues:

1, there is chance the containers crash due to random bootstrap order of containers
