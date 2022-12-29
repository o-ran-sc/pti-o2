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

This document describes how to install INF O2 service over the O-RAN INF
platform.

The audience of this document is assumed to have basic knowledge of
kubernetes CLI, and helm chart cli.

Preface
-------

In the context of hosting a RAN Application on INF, the O-RAN O2
Application provides and exposes the IMS and DMS service APIs of the O2
interface between the O-Cloud (INF) and the Service Management &
Orchestration (SMO), in the O-RAN Architecture.

The O2 interfaces enable the management of the O-Cloud (INF)
infrastructure and the deployment life-cycle management of O-RAN
cloudified NFs that run on O-Cloud (INF). See `O-RAN O2 General Aspects
and Principles
2.0 <https://orandownloadsweb.azurewebsites.net/specifications>`__, and
`INF O2
documentation <https://docs.o-ran-sc.org/projects/o-ran-sc-pti-o2/en/latest/>`__.

The O-RAN O2 application is integrated into INF as a system application.
The O-RAN O2 application package is saved in INF during system
installation, but it is not applied by default.

System administrators can follow the procedures below to install and
uninstall the O-RAN O2 application.

INF O2 Service Install
======================

1. Prerequisites
----------------

Configure the internal Ceph storage for the O2 application persistent
storage, see INF Storage Configuration and Management: `Configure the
Internal Ceph Storage
Backend <https://docs.starlingx.io/storage/kubernetes/configure-the-internal-ceph-storage-backend.html#configure-the-internal-ceph-storage-backend>`__.

Enable PVC support in ``oran-o2`` namespace, see INF Storage
Configuration and Management: `Enable ReadWriteOnce PVC Support in
Additional
Namespaces <https://docs.starlingx.io/storage/kubernetes/enable-readwriteonce-pvc-support-in-additional-namespaces.html#enable-readwriteonce-pvc-support-in-additional-namespaces>`__.

2. Procedure
------------

You can install O-RAN O2 application on INF from the command line.

1. Locate the O2 application tarball in
   ``/usr/local/share/applications/helm``.

   For example:

   ::

      /usr/local/share/applications/helm/oran-o2-<version>.tgz

2. Download ``admin_openrc.sh`` from the INF admin dashboard.

   -  Visit http://<INF dashboard address>:8080/project/api_access/
   -  Click the **Download OpenStack RC File”/”OpenStack RC File**
      button

3. Copy the file to the controller host.

4. Source the platform environment.

   ::

      $ source ./admin_openrc.sh
      ~(keystone_admin)]$

5. Upload the application.

   ::

      ~(keystone_admin)]$ system application-upload /usr/local/share/applications/helm/oran-o2-<version>.tgz

6. Prepare the override ``yaml`` file.

   1. Create a service account for SMO application.

      Create a ServiceAccount which can be used to provide SMO
      application with minimal access permission credentials.

      ::

         export SMO_SERVICEACCOUNT=smo1

         cat <<EOF > smo-serviceaccount.yaml
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

   2. Create a secret for service account and obtain an access token.

      Create a secret with the type service-account-token and pass the
      ServiceAccount in the annotation section as shown below:

      ::

         export SMO_SECRET=smo1-secret

         cat <<EOF > smo-secret.yaml
         apiVersion: v1
         kind: Secret
         metadata:
           name: ${SMO_SECRET}
           annotations:
             kubernetes.io/service-account.name: ${SMO_SERVICEACCOUNT}
         type: kubernetes.io/service-account-token
         EOF

         kubectl apply -f smo-secret.yaml

         export SMO_TOKEN_DATA=$(kubectl get secrets $SMO_SECRET -o jsonpath='{.data.token}' | base64 -d -w 0)

   3. Create certificates for the O2 service.

      Obtain an intermediate or Root CA-signed certificate and key from
      a trusted intermediate or Root Certificate Authority (CA). Refer
      to the documentation for the external Root CA that you are using
      on how to create a public certificate and private key pairs signed
      by an intermediate or Root CA for HTTPS.

      For lab purposes, see INF Security: `Create Certificates Locally
      using
      openssl <https://docs.starlingx.io/security/kubernetes/create-certificates-locally-using-openssl.html#create-certificates-locally-using-openssl>`__
      to create an Intermediate or test Root CA certificate and key, and
      use it to locally sign test certificates.

      The resulting files, from either an external CA or locally
      generated for the lab with openssl, should be:

      -  Local CA certificate - ``my-root-ca-cert.pem``
      -  Server certificate - ``my-server-cert.pem``
      -  Server key - ``my-server-key.pem``

      ..

         **Note** If using a server certificate signed by a local CA
         (i.e. lab scenario above), this local CA certificate
         (e.g. my-root-ca-cert.pem from lab scenario above) must be
         shared with the SMO application for the O2 server certificate
         verification.

   4. Prepare the O2 service application configuration file.

      As per the Cloudification and Orchestration use case defined in
      O-RAN Working Group 6, the following information should be
      generated by SMO:

      -  O-Cloud Gload ID - ``OCLOUD_GLOBAL_ID``
      -  SMO Register URL - ``SMO_REGISTER_URL``

      See `O-RAN Cloudification and Orchestration Use Cases and
      Requirements for O-RAN Virtualized
      RAN <https://orandownloadsweb.azurewebsites.net/specifications>`__.

      ::

         API_HOST_EXTERNAL_FLOATING=$(echo ${OS_AUTH_URL} | awk -F / '{print $3}' | cut -d: -f1)

         cat <<EOF > app.conf
         [DEFAULT]

         ocloud_global_id = ${OCLOUD_GLOBAL_ID}
         smo_register_url = ${SMO_REGISTER_URL}
         smo_token_data = ${SMO_TOKEN_DATA}

         [OCLOUD]
         OS_AUTH_URL = ${OS_AUTH_URL}
         OS_USERNAME = ${OS_USERNAME}
         OS_PASSWORD = ${OS_PASSWORD}
         API_HOST_EXTERNAL_FLOATING = ${API_HOST_EXTERNAL_FLOATING}

         [API]

         [WATCHER]

         [PUBSUB]
         EOF

   5. Retrieve the CA certificate from your SMO vendor.

      If the SMO application provides service via HTTPS, and the server
      certificate is self-signed, the CA certficate should be retrieved
      from the SMO.

      This procedure assumes that the name of the certificate is
      ``smo-ca.pem``

   6. Populate the override yaml file.

      Refer to the previous step for the required override values.

      ::

         APPLICATION_CONFIG=$(base64 app.conf -w 0)
         SERVER_CERT=$(base64 my-server-cert.pem -w 0)
         SERVER_KEY=$(base64 my-server-key.pem -w 0)
         SMO_CA_CERT=$(base64 smo-ca.pem -w 0)

         cat <<EOF > o2service-override.yaml

         applicationconfig: ${APPLICATION_CONFIG}
         servercrt: ${SERVER_CERT}
         serverkey: ${SERVER_KEY}
         smocacrt: ${SMO_CA_CERT}

         EOF

      To deploy other versions of an image required for a quick
      solution, to have early access to the features (eg.
      oranscinf/pti-o2imsdms:2.0.0), and to authenticate images that are
      hosted by a private registry, follow the steps below:

      1. Create a docker-registry secret in ``oran-o2`` namespace.

         ::

            export O2SERVICE_IMAGE_REG=<docker-server-endpoint>

            kubectl create secret docker-registry private-registry-key \
            --docker-server=${O2SERVICE_IMAGE_REG} --docker-username=${USERNAME} \
            --docker-password=${PASSWORD} -n oran-o2

      2. Refer to the ``imagePullSecrets`` in override file.

         ::

            cat <<EOF > o2service-override.yaml
            imagePullSecrets:
              - private-registry-key

            o2ims:
              serviceaccountname: admin-oran-o2
              images:
                tags:
                  o2service: ${O2SERVICE_IMAGE_REG}/docker.io/oranscinf/pti-o2imsdms:2.0.0
                  postgres: ${O2SERVICE_IMAGE_REG}/docker.io/library/postgres:9.6
                  redis: ${O2SERVICE_IMAGE_REG}/docker.io/library/redis:alpine
                pullPolicy: IfNotPresent
              logginglevel: "DEBUG"

            applicationconfig: ${APPLICATION_CONFIG}
            servercrt: ${SERVER_CERT}
            serverkey: ${SERVER_KEY}
            smocacrt: ${SMO_CA_CERT}

            EOF

7. Update the overrides for the oran-o2 application.

   ::

      ~(keystone_admin)]$ system helm-override-update oran-o2 oran-o2 oran-o2 --values o2service-override.yaml

      # Check the overrides
      ~(keystone_admin)]$ system helm-override-show oran-o2 oran-o2 oran-o2

8. Run the **system application-apply** command to apply the updates.

   ::

      ~(keystone_admin)]$ system application-apply oran-o2

9. Monitor the status using the command below.

   ::

      ~(keystone_admin)]$ watch -n 5 system application-list

   OR

   ::

      ~(keystone_admin)]$ watch kubectl get all -n oran-o2

3. Results
----------

You have launched services in the above namespace.

4. Postrequisites
-----------------

You will need to integrate INF with an SMO application that performs
management of O-Cloud infrastructure and the deployment life cycle
management of O-RAN cloudified NFs. See the following API reference for
details:

-  `API O-RAN O2
   interface <https://docs.o-ran-sc.org/projects/o-ran-sc-pti-o2/en/g-release/api.html>`__

INF O2 Service Uninstall
========================

.. _procedure-1:

1. Procedure
------------

You can uninstall the O-RAN O2 application on INF from the command line.

1. Uninstall the application.

   Remove O2 application related resources.

   ::

      ~(keystone_admin)]$ system application-remove oran-o2

2. Delete the application.

   Remove the uninstalled O2 application’s definition, including the
   manifest and helm charts and helm chart overrides, from the system.

   ::

      ~(keystone_admin)]$ system application-delete oran-o2

.. _results-1:

2. Results
----------

You have uninstalled the O2 application from the system.
