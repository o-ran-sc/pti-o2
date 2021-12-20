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

This document describes how to install O-RAN O2 service over O-RAN INF platform.

The audience of this document is assumed to have basic knowledge in kubernetes cli, helm chart cli.


Preface
-------

Before starting the installation and deployment of O-RAN O2 service, you should have already deployed O-RAN INF platform, and you need to download the helm charts or build from source as described in developer-guide.


ORAN O2 Service in E Release
============================

1. Provision remote cli for kubernetes over INF platform
--------------------------------------------------------


1.1 Setup Service Account over O-RAN INF platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following instruction must be done over INF platform controller host (controller-0)

-  Please see the O-RAN INF documentation to find out how to ssh to controller host of INF platform.

::

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

::

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
  NAMESPACE=orano2
  TOKEN_DATA=<TOKEN_DATA from INF>

  USER="admin-user"

  kubectl config set-cluster inf-cluster --server=https://${OAM_IP}:6443 --insecure-skip-tls-verify
  kubectl config set-credentials ${USER} --token=$TOKEN_DATA
  kubectl config  set-context ${USER}@inf-cluster --cluster=inf-cluster --user ${USER} --namespace=${NAMESPACE}
  kubectl config use-context ${USER}@inf-cluster

  kubectl get pods -A


2. Deploy O2 service
--------------------

2.1 Retrieve Helm chart for deploying of O2 service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  git clone  -b e-release "https://gerrit.o-ran-sc.org/r/pti/o2"



2.2 Prepare override yaml
~~~~~~~~~~~~~~~~~~~~~~~~~

::

  export NAMESPACE=orano2
  kubectl create ns ${NAMESPACE}

  cd /home/sysadmin/
  source /etc/platform/openrc
  cat <<EOF>o2service-override.yaml
  o2ims:
    imagePullSecrets: admin-orano2-registry-secret
    image:
      repository: registry.local:9001/admin/o2imsdms
      tag: 0.1.4
      pullPolicy: IfNotPresent
    logginglevel: "DEBUG"

  ocloud:
    OS_AUTH_URL: "${OS_AUTH_URL}"
    OS_USERNAME: "${OS_USERNAME}"
    OS_PASSWORD: "${OS_PASSWORD}"
  EOF


2.3 Deploy by helm cli
~~~~~~~~~~~~~~~~~~~~~~

::

  helm install o2service o2/charts/ -f o2service-override.yaml
  helm list |grep o2service
  kubectl -n ${NAMESPACE} get pods |grep o2service
  kubectl -n ${NAMESPACE} get services |grep o2service


2.4 Verify O2 service
~~~~~~~~~~~~~~~~~~~~~

::

  curl -k http(s)://<OAM IP>:30205
  curl -k http(s)://<OAM IP>:30205/o2ims_infrastructureInventory/v1


3 Register O-Cloud to SMO

- assumed you have setup SMO O2 endpoint for registration
- O2 service will post the O-Cloud registration data to that SMO O2 endpoint

::

  curl -k -X POST http(s)://<OAM IP>:30205/provision/smo-endpoint/v1 -d '{"smo-o2-endpoint": "<SMO O2 endpoint for registration>"}'


References
----------

- `O-RAN-SC INF`_

.. _`O-RAN-SC INF`: https://docs.o-ran-sc.org/en/latest/projects.html#infrastructure-inf
