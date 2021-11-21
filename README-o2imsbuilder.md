
## build o2ims from a container over INF


## bring up container

## Important: make sure container and host shares the same filepath to overcome local dir mounting issue

mkdir -p /home/sysadmin/share
sudo docker run -dt --privileged -v /home/sysadmin/share/:/home/sysadmin/share/ -v /var/run:/var/run --name o2imsbuilder2 centos:7

## build inside container
sudo docker exec -it o2imsbuilder2 bash

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
git clone https://opendev.org/starlingx/config.git
git clone https://opendev.org/starlingx/distcloud-client.git
cd -

docker-compose build

## test over inf host
export NAMESPACE=orano2
kubectl create ns ${NAMESPACE}

source /etc/platform/openrc
sudo docker login registry.local:9001 -u ${OS_PROJECT_NAME} -p ${OS_PASSWORD}


kubectl -n ${NAMESPACE} create secret docker-registry ${OS_PROJECT_NAME}-${NAMESPACE}-registry-secret \
--docker-server=registry.local:9001 --docker-username=${OS_PROJECT_NAME} \
--docker-password=${OS_PASSWORD} --docker-email=noreply@windriver.com

==> secret/admin-orano2-registry-secret created

sudo docker tag o2imsdms:latest registry.local:9001/admin/o2imsdms:0.1.1
sudo docker image push registry.local:9001/admin/o2imsdms:0.1.1

cd /home/sysadmin/share/o2

cat <<EOF>ocloud-override.yaml
o2ims:
  imagePullSecrets: admin-orano2-registry-secret
  image:
    repository: registry.local:9001/admin/o2imsdms
    tag: 0.1.1
    pullPolicy: IfNotPresent
  logginglevel: "DEBUG"

ocloud:
  OS_AUTH_URL: "your ocloud keystone endpoint, e.g. http://1.2.3.4:5000/v3"
  OS_USERNAME: "admin"
  OS_PASSWORD: "YourPassword"
EOF

helm install o2imstest charts/ -f ocloud-override.yaml

kubectl -n ${NAMESPACE} get pods


## issues:
