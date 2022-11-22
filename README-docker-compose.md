
# local test with docker-compose

## build images

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
git clone --depth 1 --branch r/stx.7.0 https://opendev.org/starlingx/config.git
git clone --depth 1 --branch r/stx.7.0 https://opendev.org/starlingx/distcloud-client.git

git clone --depth 1 --branch r/stx.7.0 https://opendev.org/starlingx/fault.git
cd -

docker-compose build

exit

```

## utilize a server certificates signed by a self-signed CA

~~~sh
cd o2/tests
openssl genrsa -out my-root-ca-key.pem 2048
openssl req -x509 -new -nodes -key my-root-ca-key.pem -days 1024 -out my-root-ca-cert.pem -outform PEM
openssl genrsa -out my-server-key.pem 2048
openssl req -new -key my-server-key.pem -out my-server.csr

echo subjectAltName = IP:127.0.0.1 > extfile.cnf
openssl x509 -req -in my-server.csr -CA my-root-ca-cert.pem -CAkey my-root-ca-key.pem -CAcreateserial -out my-server-cert.pem -days 365 -extfile extfile.cnf
cat my-server-cert.pem my-server-key.pem > my-server.pem

~~~

Assuming, we can get following files after performing procedure above:

Local CA certificate - my-root-ca-cert.pem
Server certificate - my-server-cert.pem
Server key - my-server-key.pem


## Bring up docker containers

~~~sh
docker-compose build
docker-compose up -d

docker ps |grep o2
docker logs -f o2_api_1
docker logs -f o2_watcher_1
~~~
