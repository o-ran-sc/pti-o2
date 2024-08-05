.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021-2024 Wind River Systems, Inc.

INF O2 Service User Guide
=========================

This guide will introduce the process that make INF O2 interface work
with SMO.

-  Assume you have an O2 service with INF platform environment, and you
   have the OAuth Server configured with the O2 service.

   .. code:: bash

      export OAM_IP=<INF_OAM_IP>

      export OAUTH2_TOKEN_ENDPOINT=http://<3rd-party OAuth Server Address>:8080/realms/master/protocol/openid-connect/token
      export OAUTH2_CLIENT_ID=<oran-o2-client-id>
      export OAUTH2_CLIENT_SECRET=<oran-o2-client-secret>

   Get berar token from the OAuth Server for request O2 application API.

   .. code:: shell

      curl -k -X POST ${OAUTH2_TOKEN_ENDPOINT} \
         -H "Content-Type: application/x-www-form-urlencoded" \
         -d "grant_type=client_credentials" \
         -d "client_id=${OAUTH2_CLIENT_ID}" \
         -d "client_secret=${OAUTH2_CLIENT_SECRET}"

   Set "access_token" value from the above step to the bash environment.
   And copy the client certificate into the bash folder that you are working on.

   .. code:: bash

      export BEARER_TOKEN=<access_token>

      ls
      client-cert.pem  client-key.pem  my-root-ca-cert.pem 

-  Discover INF platform inventory

   -  INF platform auto-discovery

      After you installed the INF O2 service, it will automatically
      discover the INF through the parameters that you give from the
      “*o2service-override.yaml*”

      The below command can get the INF platform information as O-Cloud

      .. code:: shell

         curl -X 'GET' \
           --cacert my-root-ca-cert.pem \
           --cert client-cert.pem --key client-key.pem \
           -H "Authorization: Bearer ${BEARER_TOKEN}" \
           -H 'accept: application/json'
           "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/"

   -  Resource pool

      The INF platform is a standalone environment, it has one resource
      pool. If the INF platform is a distributed cloud environment, the
      central cloud will be one resource pool, and each of the sub-cloud
      will be a resource pool. All the resources that belong to the
      cloud will be organized into the resource pool.

      Get the resource pool information through this interface

      .. code:: shell

         curl -X 'GET' \
           --cacert my-root-ca-cert.pem \
           --cert client-cert.pem --key client-key.pem \
           -H "Authorization: Bearer ${BEARER_TOKEN}" \
           -H 'accept: application/json'
           "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/resourcePools"

         # export the first resource pool id
         export resourcePoolId=`curl -k -X 'GET' --cert client-cert.pem --key client-key.pem "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/resourcePools"   -H 'accept: application/json' -H "Authorization: Bearer ${BEARER_TOKEN}" 2>/dev/null | jq .[0].resourcePoolId | xargs echo`

         echo ${resourcePoolId} # check the exported resource pool id

   -  Resource type

      Resource type defined what type is the specified resource, like a
      physical machine, memory, or CPU

      Show all resource type

      .. code:: shell

         curl -X 'GET' \
           --cacert my-root-ca-cert.pem \
           --cert client-cert.pem --key client-key.pem \
           -H "Authorization: Bearer ${BEARER_TOKEN}" \
           -H 'accept: application/json'
           "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/resourceTypes"

   -  Resource

      Get the list of all resources, the value of *resourcePoolId* from
      the result of the resource pool interface

      .. code:: shell

         curl -X 'GET' \
           --cacert my-root-ca-cert.pem \
           --cert client-cert.pem --key client-key.pem \
           -H "Authorization: Bearer ${BEARER_TOKEN}" \
           -H 'accept: application/json'
         "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/resourcePools/${resourcePoolId}/resources"

      To get the detail of one resource, need to export one specific
      resource id that wants to check

      .. code:: shell

         # export the first resource id in the resource pool
         export resourceId=`curl -k -X 'GET' --cert client-cert.pem --key client-key.pem "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/resourcePools/${resourcePoolId}/resources"   -H 'accept: application/json' -H "Authorization: Bearer ${BEARER_TOKEN}" 2>/dev/null | jq .[0].resourceId | xargs echo`

         echo ${resourceId} # check the exported resource id

         # Get the detail of one specific resource
         curl -k -X 'GET' \
         "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/resourcePools/${resourcePoolId}/resources/${resourceId}" \
         -H 'accept: application/json' -H "Authorization: Bearer ${SMO_TOKEN_DATA}"

   -  Deployment manager services endpoint

      The Deployment Manager Service (DMS) related to this IMS
      information you can use the below API to check

      .. code:: shell

         curl -X 'GET' \
           --cacert my-root-ca-cert.pem \
           --cert client-cert.pem --key client-key.pem \
           -H "Authorization: Bearer ${BEARER_TOKEN}" \
           -H 'accept: application/json'
           "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/deploymentManagers"

-  Provisioning INF platform with SMO endpoint configuration

   Assume you have an SMO, and prepare the configuration of the INF
   platform with the SMO endpoint address before the O2 service
   installation. This provisioning of the INF O2 service will make a
   request from the INF O2 service to SMO while the O2 service
   installing, which make SMO know the O2 service is working.

   After you installed the INF O2 service, it will automatically
   register the SMO through the parameters that you give from the
   “*o2app.conf*”

   .. code:: bash

      export OCLOUD_GLOBAL_ID=<Ocloud global UUID defined by SMO>
      export SMO_REGISTER_URL=<SMO Register URL for O2 service>

      cat <<EOF > o2app.conf
      [DEFAULT]

      ocloud_global_id = ${OCLOUD_GLOBAL_ID}
      smo_register_url = ${SMO_REGISTER_URL}
      ...

-  Subscribe to the INF platform resource change notification

   Assume you have an SMO, and the SMO has an API that can receive
   callback request

   -  Create a subscription to the INF O2 IMS

      .. code:: bash

         export SMO_SUBSCRIBE_CALLBACK=<The Callback URL for SMO Subscribe resource>
         export SMO_CONSUMER_SUBSCRIPTION_ID=<The Subscription ID of the SMO Consumer>

         curl -X 'POST' \
           --cacert my-root-ca-cert.pem \
           --cert client-cert.pem --key client-key.pem \
           -H "Authorization: Bearer ${BEARER_TOKEN}" \
           -H 'accept: application/json' \
           -H 'Content-Type: application/json' \
           "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/subscriptions" \
           -d '{
           "callback": "'${SMO_SUBSCRIBE_CALLBACK}'",
           "consumerSubscriptionId": "'${SMO_CONSUMER_SUBSCRIPTION_ID}'",
           "filter": ""
         }'

   -  Handle resource change notification

      When the SMO callback API gets the notification that the resource
      of INF platform changing, use the URL to get the latest resource
      information to update its database

-  Subscribe to the INF platform alarm change notification

   Assume you have an SMO, and the SMO has an API that can receive
   callback request

   -  Create an alarm subscription to the INF O2 IMS

      .. code:: bash

         export SMO_SUBSCRIBE_CALLBACK=<The Callback URL for SMO Subscribe alarm>
         export SMO_CONSUMER_SUBSCRIPTION_ID=<The Subscription ID of the SMO Consumer>

         curl -X 'POST' \
           --cacert my-root-ca-cert.pem \
           --cert client-cert.pem --key client-key.pem \
           -H "Authorization: Bearer ${BEARER_TOKEN}" \
           -H 'accept: application/json' \
           -H 'Content-Type: application/json' \
           "https://${OAM_IP}:30205/o2ims-infrastructureMonitoring/v1/alarmSubscriptions" \
           -d '{
           "callback": "'${SMO_SUBSCRIBE_CALLBACK}'",
           "consumerSubscriptionId": "'${SMO_CONSUMER_SUBSCRIPTION_ID}'",
           "filter": ""
         }'

   -  Handle alarm change notification

      When the SMO callback API gets the alarm of the INF platform, use
      the URL to get the latest alarm event record information to get
      more details

-  Use Kubernetes Control Client through O2 DMS profile

   Assume you have the kubectl command tool on your local Linux
   environment.

   And install the ‘jq’ command for your Linux bash terminal. If you are
   using Ubuntu, you can follow the below command to install it.

   .. code:: bash

      # install the 'jq' command
      sudo apt-get install -y jq

      # install 'kubectl' command
      sudo apt-get install -y apt-transport-https
      echo "deb http://mirrors.ustc.edu.cn/kubernetes/apt kubernetes-xenial main" | \
      sudo tee -a /etc/apt/sources.list.d/kubernetes.list
      gpg --keyserver keyserver.ubuntu.com --recv-keys 836F4BEB
      gpg --export --armor 836F4BEB | sudo apt-key add -
      sudo apt-get update
      sudo apt-get install -y kubectl

   We need to get the Kubernetes profile to set up the kubectl command
   tool.

   Get the DMS Id in the INF O2 service, and set it into bash
   environment.

   .. code:: bash

      # Get all DMS ID, and print them with command
      dmsIDs=$(curl -k -s -X 'GET' --cert client-cert.pem --key client-key.pem \
      "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/deploymentManagers" \
      -H 'accept: application/json' -H "Authorization: Bearer ${BEARER_TOKEN}" \
      | jq --raw-output '.[]["deploymentManagerId"]')
      for i in $dmsIDs;do echo ${i};done;

      # Choose one DMS and set it to bash environment, here I set the first one
      export dmsID=$(curl -k -s -X 'GET' --cert client-cert.pem --key client-key.pem \
        "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/deploymentManagers" \
        -H 'accept: application/json' -H "Authorization: Bearer ${BEARER_TOKEN}" \
        | jq --raw-output '.[0]["deploymentManagerId"]')

      echo ${dmsID} # check the exported DMS Id

   The profile of the ‘kubectl’ need the cluster name, I assume it is
   set to “o2dmsk8s1”.

   It also needs the server endpoint address, username, and authority,
   and for the environment that has Certificate Authority validation, it
   needs the CA data to be set up.

   .. code:: bash

      CLUSTER_NAME="o2dmsk8s1" # set the cluster name

      K8S_SERVER=$(curl -k -s -X 'GET' --cert client-cert.pem --key client-key.pem \
        "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/deploymentManagers/${dmsID}?profile=native_k8sapi" \
        -H 'accept: application/json' -H "Authorization: Bearer ${BEARER_TOKEN}" \
        | jq --raw-output '.["extensions"]["profileData"]["cluster_api_endpoint"]')
      K8S_CA_DATA=$(curl -k -s -X 'GET' --cert client-cert.pem --key client-key.pem \
        "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/deploymentManagers/${dmsID}?profile=native_k8sapi" \
        -H 'accept: application/json' -H "Authorization: Bearer ${BEARER_TOKEN}" \
        | jq --raw-output '.["extensions"]["profileData"]["cluster_ca_cert"]')

      K8S_USER_NAME=$(curl -k -s -X 'GET' --cert client-cert.pem --key client-key.pem \
        "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/deploymentManagers/${dmsID}?profile=native_k8sapi" \
        -H 'accept: application/json' -H "Authorization: Bearer ${BEARER_TOKEN}" \
        | jq --raw-output '.["extensions"]["profileData"]["admin_user"]')
      K8S_USER_CLIENT_CERT_DATA=$(curl -k -s -X 'GET' --cert client-cert.pem --key client-key.pem \
        "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/deploymentManagers/${dmsID}?profile=native_k8sapi" \
        -H 'accept: application/json' -H "Authorization: Bearer ${BEARER_TOKEN}" \
        | jq --raw-output '.["extensions"]["profileData"]["admin_client_cert"]')
      K8S_USER_CLIENT_KEY_DATA=$(curl -k -s -X 'GET' --cert client-cert.pem --key client-key.pem \
        "https://${OAM_IP}:30205/o2ims-infrastructureInventory/v1/deploymentManagers/${dmsID}?profile=native_k8sapi" \
        -H 'accept: application/json' -H "Authorization: Bearer ${BEARER_TOKEN}" \
        | jq --raw-output '.["extensions"]["profileData"]["admin_client_key"]')

      # If you do not want to set up the CA data, you can execute following command without the secure checking
      # kubectl config set-cluster ${CLUSTER_NAME} --server=${K8S_SERVER} --insecure-skip-tls-verify

      kubectl config set-cluster ${CLUSTER_NAME} --server=${K8S_SERVER}
      kubectl config set clusters.${CLUSTER_NAME}.certificate-authority-data ${K8S_CA_DATA}

      kubectl config set-credentials ${K8S_USER_NAME}
      kubectl config set users.${K8S_USER_NAME}.client-certificate-data ${K8S_USER_CLIENT_CERT_DATA}
      kubectl config set users.${K8S_USER_NAME}.client-key-data ${K8S_USER_CLIENT_KEY_DATA}

      # set the context and use it
      kubectl config set-context ${K8S_USER_NAME}@${CLUSTER_NAME} --cluster=${CLUSTER_NAME} --user ${K8S_USER_NAME}
      kubectl config use-context ${K8S_USER_NAME}@${CLUSTER_NAME}

      kubectl get ns # check the command working with this context

   Now you can use “kubectl”, which means you set up a successfully
   Kubernetes client. But, it uses the default admin user, so I
   recommend you create an account for yourself.

   Create a new user and account for K8S with a “cluster-admin” role.
   And, set the token of this user to the base environment.

   .. code:: bash

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

   Set the new user in ‘kubectl’ replace the original user, and set the
   default namespace into the context.

   .. code:: bash

      NAMESPACE=default
      TOKEN_DATA=<TOKEN_DATA from INF>

      USER="admin-user"
      CLUSTER_NAME="o2dmsk8s1"

      kubectl config set-credentials ${USER} --token=$TOKEN_DATA
      kubectl config set-context ${USER}@inf-cluster --cluster=${CLUSTER_NAME} --user ${USER} --namespace=${NAMESPACE}
      kubectl config use-context ${USER}@inf-cluster
