.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021 Wind River Systems, Inc.

INF O2 Service Overview
=======================

This project implements a reference O2 IMS and DMS service to expose INF platform to SMO via O2 interface.

In the E release, the following APIs are supported by INF O2 service:

1. O-Cloud Infrastructure Management Service

   - O-Cloud provisioning API

     - Provision SMO O2 endpoint into INF O2 service

     - O2 service discovers INF platform as O-Cloud and register INF as O-Cloud to SMO via the provisioned SMO O2 endpoint

   - O-Cloud Inventory API

     - O2 service discovers following resources of INF platform to answer queries from SMO

       - O-Cloud information

       - Resource Pool of the O-Cloud

       - Resources of the Resource Pool, including pserver, cpu, memory, port, interface

       - Resource Types associated with Resources

    - O-Cloud Subscription and Notification

      - O2 service exposes Subscription API to enable SMO subscribes to Notification of changes of resources

    - O-Cloud Deployment Management Service Endpoint discovery API

      - O2 service enables lookup of O-Cloud DMS endpoints via DeploymentManagementService resource as part of inventory

2. Deployment Management Service

   - O2 service discovers kubernetes clusters hosted by INF platform, exposes them as Deployment Management Services via O-Cloud DMS endpoints

   - The exposed DMS endpoint supports Lifecycle Management of NfDeployment which represents CNF described in helm chart, the API supports APIs below:

     - Management of NfDeploymentDescriptor

     - Management of NfDeployment
