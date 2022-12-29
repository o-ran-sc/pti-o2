.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021-2022 Wind River Systems, Inc.


Installation Guide
==================

.. contents::
   :depth: 3
   :local:

Abstract
--------

This document describes how to install INF O2 service over O-RAN INF
platform.

The audience of this document is assumed to have basic knowledge in
kubernetes cli, helm chart cli.

Preface
-------

Before starting the installation and deployment of the O-RAN O2 service,
you should have already deployed the O-RAN INF platform, and you need to
download the helm charts or build from the source as described in
developer-guide.

INF O2 Service in G Release
===========================

1. Provision remote CLI for Kubernetes over INF platform
--------------------------------------------------------

1.1 Setup Service Account over O-RAN INF platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following instruction must be done over INF platform controller host
(controller-0)

-  Please see the O-RAN INF documentation to find out how to ssh to
   controller host of INF platform.

.. code:: shell

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
   echo $TOKEN_DATA

1.2 Setup remote CLI over another Linux host (Ubuntu as an example)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following instruction should be done outside of the INF platform
controller host

.. code:: shell

   sudo apt-get install -y apt-transport-https
   echo "deb http://mirrors.ustc.edu.cn/kubernetes/apt kubernetes-xenial main" | \
   sudo tee -a /etc/apt/sources.list.d/kubernetes.list
   gpg --keyserver keyserver.ubuntu.com --recv-keys 836F4BEB
   gpg --export --armor 836F4BEB | sudo apt-key add -
   sudo apt-get update
   sudo apt-get install -y kubectl

   source <(kubectl completion bash) # setup autocomplete in bash into the current shell, bash-completion package should be installed first.
   echo "source <(kubectl completion bash)" >> ~/.bashrc # add autocomplete permanently to your bash shell.

   curl -O https://get.helm.sh/helm-v3.5.3-linux-amd64.tar.gz
   tar xvf helm-v3.5.3-linux-amd64.tar.gz
   sudo cp linux-amd64/helm /usr/local/bin/

   source <(helm completion bash)
   echo "source <(helm completion bash)" >> ~/.bashrc

   OAM_IP=<INF OAM IP>
   NAMESPACE=oran-o2
   TOKEN_DATA=<TOKEN_DATA from INF>

   USER="admin-user"

   kubectl config set-cluster inf-cluster --server=https://${OAM_IP}:6443 --insecure-skip-tls-verify
   kubectl config set-credentials ${USER} --token=$TOKEN_DATA
   kubectl config set-context ${USER}@inf-cluster --cluster=inf-cluster --user ${USER} --namespace=${NAMESPACE}
   kubectl config use-context ${USER}@inf-cluster

   kubectl get pods -A


2. Deploy INF O2 service
------------------------

2.1 Retrieve Helm chart for deploying of INF O2 service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   git clone -b g-release "https://gerrit.o-ran-sc.org/r/pti/o2"

2.2 Prepare override yaml
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   export NAMESPACE=oran-o2
   kubectl create ns ${NAMESPACE}

   export OS_AUTH_URL=<INF OAM Auth URL e.g.: http://OAM_IP:5000/v3>
   export OS_USERNAME=<INF username e.g.: admin>
   export OS_PASSWORD=<INF password for user e.g.: adminpassword>

   # If the external OAM IP same as OS_AUTH_URL's IP address, you can use the below command to set the environment
   # export API_HOST_EXTERNAL_FLOATING=$(echo ${OS_AUTH_URL} | sed -e s,`echo ${OS_AUTH_URL} | grep :// | sed -e's,^\(.*//\).*,\1,g'`,,g | cut -d/ -f1 | sed -e 's,:.*,,g')
   export API_HOST_EXTERNAL_FLOATING=<INF external_oam_floating_address e.g.: 128.10.10.10>

   # please specify the smo service account yaml file
   export SMO_SERVICEACCOUNT=<your input here eg.: smo>
   # service account and binding for smo yaml file

   cat <<EOF >smo-serviceaccount.yaml
   apiVersion: rbac.authorization.k8s.io/v1
   kind: Role
   metadata:
     namespace: default
     name: pod-reader
   rules:
   - apiGroups: [""] # "" indicates the core API group
     resources: ["pods"]
     verbs: ["get", "watch", "list"]
   ---
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: ${SMO_SERVICEACCOUNT}
     namespace: default
   ---
   apiVersion: rbac.authorization.k8s.io/v1
   kind: RoleBinding
   metadata:
     name: read-pods
     namespace: default
   roleRef:
     apiGroup: rbac.authorization.k8s.io
     kind: Role
     name: pod-reader
   subjects:
   - kind: ServiceAccount
     name: ${SMO_SERVICEACCOUNT}
     namespace: default

   EOF

   kubectl apply -f smo-serviceaccount.yaml

   #export the smo account token data
   export SMO_SECRET=$(kubectl -n default get serviceaccounts $SMO_SERVICEACCOUNT -o jsonpath='{.secrets[0].name}')
   export SMO_TOKEN_DATA=$(kubectl -n default get secrets $SMO_SECRET -o jsonpath='{.data.token}')

   #prepare the application config file
   cat <<EOF >app.conf
   [DEFAULT]

   ocloud_global_id = 4e24b97c-8c49-4c4f-b53e-3de5235a4e37

   smo_register_url = http://127.0.0.1:8090/register
   smo_token_data = ${SMO_TOKEN_DATA}

   [OCLOUD]
   OS_AUTH_URL: ${OS_AUTH_URL}
   OS_USERNAME: ${OS_USERNAME}
   OS_PASSWORD: ${OS_PASSWORD}
   API_HOST_EXTERNAL_FLOATING: ${API_HOST_EXTERNAL_FLOATING}

   [API]

   [WATCHER]

   [PUBSUB]

   EOF

   #prepare the ssl cert files or generate with below command.

   PARENT="imsserver"
   openssl req \
   -x509 \
   -newkey rsa:4096 \
   -sha256 \
   -days 365 \
   -nodes \
   -keyout $PARENT.key \
   -out $PARENT.crt \
   -subj "/CN=${PARENT}" \
   -extensions v3_ca \
   -extensions v3_req \
   -config <( \
     echo '[req]'; \
     echo 'default_bits= 4096'; \
     echo 'distinguished_name=req'; \
     echo 'x509_extension = v3_ca'; \
     echo 'req_extensions = v3_req'; \
     echo '[v3_req]'; \
     echo 'basicConstraints = CA:FALSE'; \
     echo 'keyUsage = nonRepudiation, digitalSignature, keyEncipherment'; \
     echo 'subjectAltName = @alt_names'; \
     echo '[ alt_names ]'; \
     echo "DNS.1 = www.${PARENT}"; \
     echo "DNS.2 = ${PARENT}"; \
     echo '[ v3_ca ]'; \
     echo 'subjectKeyIdentifier=hash'; \
     echo 'authorityKeyIdentifier=keyid:always,issuer'; \
     echo 'basicConstraints = critical, CA:TRUE, pathlen:0'; \
     echo 'keyUsage = critical, cRLSign, keyCertSign'; \
     echo 'extendedKeyUsage = serverAuth, clientAuth')


   applicationconfig=`base64 app.conf -w 0`
   servercrt=`base64 imsserver.crt -w 0`
   serverkey=`base64 imsserver.key -w 0`
   smocacrt=`base64 smoca.crt -w 0`

   echo $applicationconfig
   echo $servercrt
   echo $serverkey
   echo $smocacrt


   cat <<EOF>o2service-override.yaml
   imagePullSecrets:
     - default-registry-key

   o2ims:
     serviceaccountname: admin-oran-o2
     images:
       tags:
         o2service: nexus3.o-ran-sc.org:10004/o-ran-sc/pti-o2imsdms:2.0.0
         postgres: docker.io/library/postgres:9.6
         redis: docker.io/library/redis:alpine
       pullPolicy: IfNotPresent
     logginglevel: "DEBUG"

   applicationconfig: ${applicationconfig}
   servercrt: ${servercrt}
   serverkey: ${serverkey}
   smocacrt: ${smocacrt}

   EOF

   cat o2service-override.yaml

2.3 Deploy by helm cli
~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   helm install o2service o2/charts -f o2service-override.yaml
   helm list |grep o2service
   kubectl -n ${NAMESPACE} get pods |grep o2api
   kubectl -n ${NAMESPACE} get services |grep o2api

2.4 Verify INF O2 service
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

   curl -k http(s)://<OAM IP>:30205/o2ims_infrastructureInventory/v1/

2.5 INF O2 Service API Swagger
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Swagger UI can be found with URL: http(s)://<OAM IP>:30205

References
----------

- `O-RAN-SC INF`_

.. _`O-RAN-SC INF`: https://docs.o-ran-sc.org/en/latest/projects.html#infrastructure-inf
