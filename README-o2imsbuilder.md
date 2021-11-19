
## build o2ims from a container over INF


## bring up container

## Important: make sure container and host shares the same filepath to overcome local dir mounting issue

mkdir -p /home/sysadmin/share
sudo docker run -dt --privileged -v /home/sysadmin/share/:/home/sysadmin/share/ -v /var/run:/var/run --name o2imsbuilder2 centos:7
sudo docker exec -it o2imsbuilder2 bash

## build inside container

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
sudo docker tag o2imsdms:latest registry.local:9001/o2imsdms:latest

sudo docker image push registry.local:9001/o2imsdms:latest

## issues:
