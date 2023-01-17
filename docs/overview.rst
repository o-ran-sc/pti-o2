.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021 Wind River Systems, Inc.

INF O2 Service Overview
=======================

This project implements a reference O-RAN O2 IMS and DMS service to expose the INF platform to SMO via the O-RAN O2 interface.

In the F release, the following APIs are supported by the INF O2 service:

1. INF O2 service Infrastructure Management Service (IMS)

   - INF O2 service provisioning API

     - Provision SMO O2 endpoint into INF O2 service

     - O2 service discovers INF platform and registers INF platform to SMO via the provisioned SMO O2 endpoint

   - INF O2 service Inventory API

     - O2 service discovers following resources of INF platform to answer queries from SMO

       - INF platform information

       - Resource Pool of the INF platform

       - Resources of the Resource Pool, including pserver, cpu, memory, port, interface

       - Resource Types associated with Resources

    - INF platform Subscription and Notification

      - INF O2 service exposes Subscription API to enable SMO subscribes to Notification of changes of resources

    - INF platform Deployment Management Service Endpoint discovery API

      - INF O2 service enables lookup of INF O2 DMS endpoints via DeploymentManagementService resource as part of inventory

2. INF O2 service Deployment Management Service (DMS)

   - INF O2 service discovers kubernetes clusters hosted by INF platform, exposes them as Deployment Management Services via DMS endpoints

   - The exposed DMS endpoint supports Lifecycle Management of NfDeployment which represents CNF described in helm chart, the API supports APIs below:

     - Management of NfDeploymentDescriptor

     - Management of NfDeployment
