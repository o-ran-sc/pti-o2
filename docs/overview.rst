.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. Copyright (C) 2021 Wind River Systems, Inc.

INF O2 Service Overview
=======================

This project implements a reference O2 IMS and DMS service to expose O2 interface to SMO.

In the E release, the following API of O2 interface is enabled:

1. O-Cloud registration and inventory query

   - O2 service discovers INF platform as O-Cloud, register the O-Cloud to SMO with provisioned SMO O2 endpoint.
   
     - Provision SMO O2 endpoint

     - Register INF as O-Cloud to SMO via SMO O2 endpoint

   - O2 service discovers following resources of INF platform to answer queries from SMO

     - O-Cloud information

     - Resource Pool of the O-Cloud

     - Resources of the Resource Pool, including pserver, cpu, memory, port, interface

     - kubernetes API endpoint as Deployment Management Service


2. Deployment Management Service

   - O2 service expose DMS on behalf of kubernetes API endpoint hosted by INF platform, which support NfDeployment described by Helm charts
   
     - Management of NfDeploymentDescriptor

     - Management of NfDeployment


3. Subscription and Notification

   - O2 service exposes Subscription API to enable SMO subscribes to Notification of changes of resources

     - Management of Subscriptions

     - Notification delivery via Rest API provided by specific Subscriptions
