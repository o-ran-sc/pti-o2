.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021 Wind River Systems, Inc.

INF O2 Service User Guide
=========================

This guide will introduce the process that make INF O2 interface work with
SMO.

-  Assume you have an O2 service with INF platform environment

   .. code:: bash

      export OAM_IP=<INF_OAM_IP>

-  Discover INF platform inventory

   -  INF platform auto discovery

      After you installed the INF O2 service, it will automatically
      discover the INF through the parameters that you give from the
      “*o2service-override.yaml*”

      Below command can get the INF platform information as O-Cloud

      .. code:: shell

         curl -X 'GET' \
           "http://${OAM_IP}:30205/o2ims_infrastructureInventory/v1/" \
           -H 'accept: application/json'

   -  Resource pool

      One INF platform have one resource pool, all the resources that belong
      to this INF platform will be organized into this resource pool

      Get the resource pool information through this interface

      .. code:: shell

         curl -X 'GET' \
           "http://${OAM_IP}:30205/o2ims_infrastructureInventory/v1/resourcePools" \
           -H 'accept: application/json'

         # export resource pool id
         export resourcePoolId=`curl -X 'GET'   "http://${OAM_IP}:30205/o2ims_infrastructureInventory/v1/resourcePools"   -H 'accept: application/json' -H 'X-Fields: resourcePoolId' 2>/dev/null | jq .[].resourcePoolId | xargs echo`

         echo ${resourcePoolId} # check the exported resource pool id

   -  Resource type

      Resource type defined what type is the specified resource, like a
      physical machine, memory, or CPU

      Show all resource type

      .. code:: shell

         curl -X 'GET' \
           "http://${OAM_IP}:30205/o2ims_infrastructureInventory/v1/resourceTypes" \
           -H 'accept: application/json'

   -  Resource

      Get the list of all resources, the value of *resourcePoolId* from
      the result of resource pool interface

      .. code:: shell

         curl -X 'GET' \
           "http://${OAM_IP}:30205/o2ims_infrastructureInventory/v1/resourcePools/${resourcePoolId}/resources" \
           -H 'accept: application/json'

      Get detail of one resource, need to export one specific resource
      id that wants to check

      .. code:: shell

         curl -X 'GET' \
           "http://${OAM_IP}:30205/o2ims_infrastructureInventory/v1/resourcePools/${resourcePoolId}/resources/${resourceId}" \
           -H 'accept: application/json'

   -  Deployment manager services endpoint

      The Deployment Manager Service (DMS) that related to this IMS
      information you can use below API to check

      .. code:: shell

         curl -X 'GET' \
           "http://${OAM_IP}:30205/o2ims_infrastructureInventory/v1/deploymentManagers" \
           -H 'accept: application/json'

-  Provisioning INF platform with SMO endpoint configuration

   Assume you have an SMO, then configure INF platform with SMO endpoint
   address. This provisioning of INF O2 service will make a request from
   INF O2 service to SMO, that make SMO know the O2 service is working.

   It needs SMO to have an API like
   “*http(s)://SMO_HOST:SMO_PORT/registration*”, which can accept JSON
   format data.

   .. code:: bash

      curl -X 'POST' \
        'http://'${OAM_IP}':30205/provision/v1/smo-endpoint' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "endpoint": "http://<SMO_HOST>:<SMO_PORT>/registration"
      }'

-  Subscribe to the INF platform resource change notification

   Assume you have an SMO, and the SMO have an API can be receive
   callback request

   -  Create subscription in the INF O2 IMS

      .. code:: bash

         curl -X 'POST' \
           "http://${OAM_IP}:30205/o2ims_infrastructureInventory/v1/subscriptions" \
           -H 'accept: application/json' \
           -H 'Content-Type: application/json' \
           -d '{
           "callback": "http://SMO/address/to/callback",
           "consumerSubscriptionId": "<ConsumerIdHelpSmoToIdentify>",
           "filter": "<ResourceTypeNameSplitByComma,EmptyToGetAll>"
         }'

   -  Handle resource change notification

      When the SMO callback API get the notification that the resource
      of INF platform changing, use the URL to get the latest resource
      information to update its database

-  Orchestrate CNF in helm chart

   On this sample, we prepare a firewall chart to test the
   orchestration.

   We need to do some preparation to make the helm repo work and include
   our firewall chart inside of the repository.

      Get the DMS Id in the INF O2 service, and set it into bash environment

      .. code:: bash

         curl --location --request GET "http://${OAM_IP}:30205/o2ims_infrastructureInventory/v1/deploymentManagers"

         export dmsId=`curl --location --request GET "http://${OAM_IP}:30205/o2ims_infrastructureInventory/v1/deploymentManagers" 2>/dev/null | jq .[].deploymentManagerId | xargs echo`

         echo ${dmsId} # check the exported DMS id

      Using helm to deploy a chartmuseum to the INF platform

      .. code:: bash

         helm repo add chartmuseum https://chartmuseum.github.io/charts
         helm repo update
         helm pull chartmuseum/chartmuseum # download chartmuseum-3.4.0.tgz to local
         tar zxvf chartmuseum-3.4.0.tgz
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

      Update the helm repo and add the chartmusem into the repository

      .. code:: bash

         helm repo add o2imsrepo http://${NODE_IP}:30330
         helm repo update

      Download the firewall chart and push it into the repository

      .. code:: bash

         git clone https://github.com/biny993/firewall-host-netdevice.git
         tar -zcvf firewall-host-netdevice-1.0.0.tgz firewall-host-netdevice/
         helm plugin install https://github.com/chartmuseum/helm-push.git
         helm cm-push firewall-host-netdevice-1.0.0.tgz o2imsrepo
         helm repo update
         helm search repo firewall

      Setup host net device over INF node

      .. code:: bash

         ssh sysadmin@<INF OAM IP>
         sudo ip link add name veth11 type veth peer name veth12
         sudo ip link add name veth21 type veth peer name veth22
         sudo ip link |grep veth
         exit

   -  Create NfDeploymentDescriptor on the INF O2 DMS

      .. code:: bash

         curl --location --request POST "http://${OAM_IP}:30205/o2dms/v1/${dmsId}/O2dms_DeploymentLifecycle/NfDeploymentDescriptor" \
         --header 'Content-Type: application/json' \
         --data-raw '{
           "name": "cfwdesc1",
           "description": "demo nf deployment descriptor",
           "artifactRepoUrl": "http://'${NODE_IP}':30330",
           "artifactName": "firewall-host-netdevice",
           "inputParams": 
           "{\n  \"image\": {\n    \"repository\": \"ubuntu\",\n    \"tag\": 18.04,\n    \"pullPolicy\": \"IfNotPresent\"\n  },\n  \"resources\": {\n    \"cpu\": 2,\n    \"memory\": \"2Gi\",\n    \"hugepage\": \"0Mi\",\n    \"unprotectedNetPortVpg\": \"veth11\",\n    \"unprotectedNetPortVfw\": \"veth12\",\n    \"unprotectedNetCidr\": \"10.10.1.0/24\",\n    \"unprotectedNetGwIp\": \"10.10.1.1\",\n    \"protectedNetPortVfw\": \"veth21\",\n    \"protectedNetPortVsn\": \"veth22\",\n    \"protectedNetCidr\": \"10.10.2.0/24\",\n    \"protectedNetGwIp\": \"10.10.2.1\",\n    \"vfwPrivateIp0\": \"10.10.1.1\",\n    \"vfwPrivateIp1\": \"10.10.2.1\",\n    \"vpgPrivateIp0\": \"10.10.1.2\",\n    \"vsnPrivateIp0\": \"10.10.2.2\"\n  }\n}",
           "outputParams": "{\"output1\": 100}"
         }'

         curl --location --request GET "http://${OAM_IP}:30205/o2dms/v1/${dmsId}/O2dms_DeploymentLifecycle/NfDeploymentDescriptor"

         export descId=` curl -X 'GET'   "http://${OAM_IP}:30205/o2dms/v1/${dmsId}/O2dms_DeploymentLifecycle/NfDeploymentDescriptor"   -H 'accept: application/json'   -H 'X-Fields: id' 2>/dev/null | jq .[].id | xargs echo`

         echo ${descId} # check the exported descriptor id

   -  Create NfDeployment on the INF O2 DMS

      When you have an descriptor of deployment, you can create a
      NfDeployment, it will trigger an event inside of the IMS/DMS, and
      use the K8S API to create a real pod of the firewall sample

      .. code:: bash

         curl --location --request POST "http://${OAM_IP}:30205/o2dms/v1/${dmsId}/O2dms_DeploymentLifecycle/NfDeployment" \
         --header 'Content-Type: application/json' \
         --data-raw '{
           "name": "cfw100",
           "description": "demo nf deployment",
           "descriptorId": "'${descId}'",
           "parentDeploymentId": ""
         }'

         curl --location --request GET "http://${OAM_IP}:30205/o2dms/v1/${dmsId}/O2dms_DeploymentLifecycle/NfDeployment"

   -  Check pods of the firewall sample

      .. code:: bash

         kubectl get pods

   -  Delete the deployment we just created

      .. code:: shell

         export NfDeploymentId=`curl --location --request GET "http://${OAM_IP}:30205/o2dms/v1/${dmsId}/O2dms_DeploymentLifecycle/NfDeployment" 2>/dev/null | jq .[].id | xargs echo`

         echo ${NfDeploymentId} # Check the exported deployment id

         curl --location --request DELETE "http://${OAM_IP}:30205/o2dms/v1/${dmsId}/O2dms_DeploymentLifecycle/NfDeployment/${NfDeploymentId}"
