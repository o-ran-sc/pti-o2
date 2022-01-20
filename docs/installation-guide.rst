.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021 Wind River Systems, Inc.


Installation Guide
==================

.. contents::
   :depth: 3
   :local:

Abstract
--------

This document describes how to install INF O2 service over O-RAN INF platform.

The audience of this document is assumed to have basic knowledge in kubernetes cli, helm chart cli.


Preface
-------

Before starting the installation and deployment of O-RAN O2 service, you should have already deployed O-RAN INF platform, and you need to download the helm charts or build from source as described in developer-guide.


INF O2 Service in E Release
===========================

1. Provision remote cli for kubernetes over INF platform
--------------------------------------------------------


1.1 Setup Service Account over O-RAN INF platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following instruction must be done over INF platform controller host (controller-0)

-  Please see the O-RAN INF documentation to find out how to ssh to controller host of INF platform.

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


1.2 Setup remote cli over another linux host (ubuntu as example)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following instruction should be done outside of INF platform controller host

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
  NAMESPACE=orano2
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

  git clone -b e-release "https://gerrit.o-ran-sc.org/r/pti/o2"



2.2 Prepare override yaml
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

  export NAMESPACE=orano2
  kubectl create ns ${NAMESPACE}

  # default kube config location is ~/.kube/config
  cp ~/.kube/config o2/charts/resources/scripts/init/k8s_kube.conf

  export OS_AUTH_URL=<INF OAM Auth URL e.g.: http://OAM_IP:5000/v3>
  export OS_USERNAME=<INF username e.g.: admin>
  export OS_PASSWORD=<INF password for user e.g.: adminpassword>

  # If the external OAM IP same as OS_AUTH_URL's IP address, you can use the below command to set the environment
  # export API_HOST_EXTERNAL_FLOATING=$(echo ${OS_AUTH_URL/$(echo ${OS_AUTH_URL} | grep :// | sed -e's,^\(.*//\).*,\1,g')} | cut -d/ -f1 | sed -e 's,:.*,,g')
  export API_HOST_EXTERNAL_FLOATING=<INF external_oam_floating_address e.g.: 128.10.10.10>

  cat <<EOF>o2service-override.yaml
  o2ims:
    imagePullSecrets: admin-orano2-registry-secret
    image:
      repository: nexus3.o-ran-sc.org:10004/o-ran-sc/pti-o2imsdms
      tag: 1.0.0
      pullPolicy: IfNotPresent
    logginglevel: "DEBUG"

  ocloud:
    OS_AUTH_URL: "${OS_AUTH_URL}"
    OS_USERNAME: "${OS_USERNAME}"
    OS_PASSWORD: "${OS_PASSWORD}"
    K8S_KUBECONFIG: "/opt/k8s_kube.conf"
    API_HOST_EXTERNAL_FLOATING: "${API_HOST_EXTERNAL_FLOATING}"
  EOF


2.3 Deploy by helm cli
~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

  helm install o2service o2/charts/ -f o2service-override.yaml
  helm list |grep o2service
  kubectl -n ${NAMESPACE} get pods |grep o2service
  kubectl -n ${NAMESPACE} get services |grep o2service


2.4 Verify INF O2 service
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

  curl -k http(s)://<OAM IP>:30205/o2ims_infrastructureInventory/v1/


2.5 INF O2 Service API Swagger 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Swagger UI can be found with URL: http(s)://<OAM IP>:30205
                 

3. Register INF O2 Service to SMO
---------------------------------

- assumed you have setup SMO O2 endpoint for registration
- INF O2 service will post the INF platform registration data to that SMO O2 endpoint


.. code:: shell

  curl -X 'GET' \
  'http(s)://<OAM IP>:30205/provision/v1/smo-endpoint' \
  -H 'accept: application/json'

  curl -k -X 'POST' \
    'http(s)://<OAM IP>:30205/provision/v1/smo-endpoint' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"endpoint": "<SMO O2 endpoint for registration>"}'

  # Confirm SMO endpoint provision status
  curl -X 'GET' \
  'http(s)://<OAM IP>:30205/provision/v1/smo-endpoint' \
  -H 'accept: application/json'


References
----------

- `O-RAN-SC INF`_

.. _`O-RAN-SC INF`: https://docs.o-ran-sc.org/en/latest/projects.html#infrastructure-inf
