.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021 Wind River Systems, Inc.

O-Cloud O2 Service User Guide
=============================

This guide will introduce the process that make O2 interface work with
SMO.

-  Assume you have an O-Cloud O2 environment

-  Discover O-Cloud inventory

   -  O-Cloud auto discovery

      After you installed the O-Cloud service, it will automatically
      discover the INF through the parameters that you give from the
      “*o2service-override.yaml*”

      Below command can get the O-Cloud information

      .. code:: shell

         curl -X 'GET' \
           'http://<OAM IP>:30205/o2ims_infrastructureInventory/v1/' \
           -H 'accept: application/json'

   -  Resource pool

      One O-Cloud have one resource pool, all the resources that belong
      to this O-Cloud will be organized into this resource pool

      Get the resource pool information through this interface

      .. code:: shell

         curl -X 'GET' \
           'http://<OAM IP>:30205/o2ims_infrastructureInventory/v1/resourcePools' \
           -H 'accept: application/json'

   -  Resource type

      Resource type defined what type is the specified resource, like a
      physical machine, memory, or CPU

      Show all resource type

      .. code:: shell

         curl -X 'GET' \
           'http://<OAM IP>:30205/o2ims_infrastructureInventory/v1/resourceTypes' \
           -H 'accept: application/json'

   -  Resource

      Get the list of all resources, the value of *resourcePoolId* from
      the result of resource pool interface

      .. code:: shell

         curl -X 'GET' \
           "http://<OAM IP>:30205/o2ims_infrastructureInventory/v1/resourcePools/${resourcePoolId}/resources" \
           -H 'accept: application/json'

      Get detail of one resource

      .. code:: shell

         curl -X 'GET' \
           "http://<OAM IP>:30205/o2ims_infrastructureInventory/v1/resourcePools/${resourcePoolId}/resources/${resourceId}" \
           -H 'accept: application/json'

   -  Deployment manager services endpoint

      The Deployment Manager Service (DMS) that related to this IMS
      information you can use below API to check

      .. code:: shell

         curl -X 'GET' \
           'http://<OAM IP>:30205/o2ims_infrastructureInventory/v1/deploymentManagers' \
           -H 'accept: application/json'

-  Subscribe to the O-Cloud resource change notification

   Assume you have a SMO, and the SMO have an API can be receive
   callback request

   -  Create subscription in O-Cloud IMS

      .. code:: bash

         curl -X 'POST' \
           'http://<OAM IP>:30205/o2ims_infrastructureInventory/v1/subscriptions' \
           -H 'accept: application/json' \
           -H 'Content-Type: application/json' \
           -d '{
           "callback": "http://SMO/address/to/callback",
           "consumerSubscriptionId": "<ConsumerIdHelpSmoToIdentify>",
           "filter": "<ResourceTypeNameSplitByComma,EmptyToGetAll>"
         }'

   -  Handle resource change notification

      When the SMO callback API get the notification that the resource
      of O-Cloud changing, use the URL to get the latest resource
      information to update its database

-  Orchestrate CNF in helm chart

   On this sample, we prepare a firewall chart to test the
   orchestration.

   We need to do some preparation to make the helm repo work and include
   our firewall chart inside of the repository.

      Get the DMS Id in the O-Cloud, and set it into bash environment

      .. code:: bash

         curl --location --request GET 'http://<OAM IP>:30205/o2ims_infrastructureInventory/v1/deploymentManagers'

         export dmsId=`curl --location --request GET 'http://<OAM IP>:30205/o2ims_infrastructureInventory/v1/deploymentManagers' 2>/dev/null | jq .[].deploymentManagerId | xargs echo`

      Using helm to deploy a chartmuseum to the INF

      .. code:: bash

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
         helm push firewall-host-netdevice-1.0.0.tgz o2imsrepo
         helm repo update
         helm search repo firewall

   -  Create NfDeploymentDescriptor

      .. code:: bash

         curl --location --request POST "http://<OAM IP>:30205/o2dms/${dmsId}/O2dms_DeploymentLifecycle/NfDeploymentDescriptor" \
         --header 'Content-Type: application/json' \
         --data-raw '{
           "name": "cfwdesc1",
           "description": "demo nf deployment descriptor",
           "artifactRepoUrl": "http://${NODE_IP}:30330",
           "artifactName": "firewall-host-netdevice",
           "inputParams": 
           "{\n  \"image\": {\n    \"repository\": \"ubuntu\",\n    \"tag\": 18.04,\n    \"pullPolicy\": \"IfNotPresent\"\n  },\n  \"resources\": {\n    \"cpu\": 2,\n    \"memory\": \"2Gi\",\n    \"hugepage\": \"256Mi\",\n    \"unprotectedNetPortVpg\": \"veth11\",\n    \"unprotectedNetPortVfw\": \"veth12\",\n    \"unprotectedNetCidr\": \"10.10.1.0/24\",\n    \"unprotectedNetGwIp\": \"10.10.1.1\",\n    \"protectedNetPortVfw\": \"veth21\",\n    \"protectedNetPortVsn\": \"veth22\",\n    \"protectedNetCidr\": \"10.10.2.0/24\",\n    \"protectedNetGwIp\": \"10.10.2.1\",\n    \"vfwPrivateIp0\": \"10.10.1.1\",\n    \"vfwPrivateIp1\": \"10.10.2.1\",\n    \"vpgPrivateIp0\": \"10.10.1.2\",\n    \"vsnPrivateIp0\": \"10.10.2.2\"\n  }\n}",
           "outputParams": "{\"output1\": 100}"
         }'

         curl --location --request GET "http://<OAM IP>:30205/o2dms/${dmsId}/O2dms_DeploymentLifecycle/NfDeploymentDescriptor"

   -  Create NfDeployment

      When you have an descriptor of deployment, you can create a
      NfDeployment, it will trigger an event inside of the IMS/DMS, and
      use the K8S API to create a real pod of the firewall sample

      .. code:: bash

         curl --location --request POST "http://<OAM IP>:30205/o2dms/${dmsId}/O2dms_DeploymentLifecycle/NfDeployment" \
         --header 'Content-Type: application/json' \
         --data-raw '{
           "name": "cfw100",
           "description": "demo nf deployment",
           "descriptorId": "<Descriptor ID>",
           "parentDeploymentId": ""
         }'

         curl --location --request GET "http://<OAM IP>:30205/o2dms/${dmsId}/O2dms_DeploymentLifecycle/NfDeployment"

   -  Check pods of the firewall sample

      .. code:: bash

         kubectl get pods

   -  Delete the deployment we just created

      .. code:: shell

         export NfDeploymentId=`curl --location --request GET 'http://<OAM IP>:30205/o2dms/${dmsId}/O2dms_DeploymentLifecycle/NfDeployment' 2>/dev/null | jq .[].id | xargs echo`

         curl --location --request DELETE "http://<OAM IP>:30205/o2dms/${dmsId}/O2dms_DeploymentLifecycle/NfDeployment/${NfDeploymentId}"
