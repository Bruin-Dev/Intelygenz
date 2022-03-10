<div align="center">
<img src="https://media.licdn.com/dms/image/C4E0BAQHrME9aCW6ulg/company-logo_200_200/0?e=2159024400&v=beta&t=6xMNS1zK1F8asBlM16EzbJ4Im7SlQ8L7a7sgcaNzZQE"  width="200" height="200">
</div>

# Context

Configurations are stored in [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html).

Parameter Store is a capability of AWS Systems Manager that allows storing configuration values in hierarchical structures. It also provides the ability to encrypt
these values through [AWS KMS](https://aws.amazon.com/kms/) keys, and allows keeping track of configuration changes / versions for auditing purposes.

From a pricing perspective, parameters can be defined either as **simple** or **advanced**:
- **Simple**. This kind of parameters come with no additional charges, and can hold up to 4KB of data. Parameter Store allows defining up to 10,000 simple parameters
  per account and region.
- **Advanced**. AWS charges $0.05 per advanced parameter per month. These can hold up to 8KB of data, and Parameter Store allows defining up to 100,000 of them
  per account and region.

Attending to their type, parameters can be defined as:
* **String**. These parameters consist of a block of text. Nothing else.
* **StringList**. These parameters hold comma-separated values, but bear in mind that this is just a convention. AWS will **not** turn the value into an array before
  returning it through Parameter Store API; that is, it will be kept as a string.
* **SecureString**. Essentially, these are the same as **String** parameters, but empowered with encryption features thanks to KMS keys.

# Conventions

Please, take some time to go through the following conventions before publishing new parameters to Parameter Store.

## Parameter names

Any new configuration published to Parameter Store must match the following pattern:

```
/automation-engine/<environment>/<service-name>/<parameter>
```

where:
* **environment** refers to the Kubernetes context whose namespaces will take this parameter. Allowed values are `dev` and `pro`.
* **service-name** refers to the name of the service this parameter will be loaded to. Examples of allowed values would be `bruin-bridge`,
  `tnba-monitor`, `repair-tickets-monitor`, and so on.
* **parameter** refers to the name of the parameter that will be loaded to the service through an environment variable.

Most configurations will follow the previous pattern, but if the business logic of a service carries out several tasks related to the same
domain concept, an alternate form can be used:

```
/automation-engine/<environment>/<domain>/<task>/<parameter>
```

where:
* **domain** refers to a domain concept that can represent multiple tasks accurately. An example would be `service-affecting`,
  which is a domain area that represents strongly related tasks (in this case, tasks related to Service Affecting troubles).
* **task** refers to the underlying piece of logic that is independent of other tasks, but is still suitable to have under the
  subpath defined by `domain`. Considering that `domain` is set to `service-affecting`, acceptable values for `task` would be
  `monitor`, `daily-bandwidth-report`, or `reoccurring-trouble-report`.

As a rule of thumb, choose the first pattern to name parameters if possible. However, if there is a strong
reason to choose the second pattern over the first one, that is totally fine.

If there are doubts about choosing one or the other, it can be brought up to discussion with the rest of the team.

## Values

Before getting into how to define new configurations, bear these considerations in mind  to keep certain consistency and avoid confusion / potential errors:
* Values representing a time duration **must** always be expressed in seconds.
  * `24` should not be used to represent the hours in a period of 1 day.
  * `86400` should be used to represent the hours in a period of 1 day.

* Values representing percentages **must** always be expressed in their integer form.
  * `0.75` should not be used to represent the value `75%`.
  * `75` should be used to represent the value `75%`.
  
* JSON-like values **must** adhere to the [JSON specification](https://www.json.org/json-en.html). The most relevant considerations are:
  1. All keys in an object-like JSON must be strings, even if they represent numbers.
  
     Example:
     ```json
     // NOT valid
     {
         1: "foo",
         2: "bar"
     }
     
     // Valid
     {
         "1": "foo",
         "2": "bar"
     }

     // Valid
     {
         "foo": "bar",
         "baz": "hey"
     }
     ```
  2. An array-like JSON can hold a combination of values with different types, be them integers, floats, boolean, arrays, objects, and so on.

     Example:
     ```json
     [
         1,
         "foo",
         0.75,
         "2",
         "bar",
         true,
         [
            "hello",
            "world"
         ],
         {
            "hello": "world"
         }
     ]
     ```

* Consider prettifying JSON-like configurations before publishing to Parameter Store. This enhances readability when
  dealing with huge JSONs.

**Developers are responsible for making any necessary transformations related to data types, time conversions, etc. in the config files
of a particular service**.

## Encryption

A parameter must be encrypted if it holds:
* Personally Identifiable Information. This includes e-mail addresses, names, surnames, phone numbers, and so on.
* Authentication credentials of any kind.
* URLs from third party services.
* Information related to application domains, such as:
  * IDs (even incremental ones)
  * Organization names
  * Domain-related values that potentially expose internal details about third party systems

# Publishing configurations to Parameter Store

Adding new configurations to Parameter Store is pretty straightforward. The process should be as easy as:
1. Access the AWS Management Console.
2. Go to the AWS Systems Manager Parameter Store dashboard.
3. Hit `Create parameter`.
4. Give the parameter a `Name` that complies with any of the patterns under the [Parameter names](#parameter-names) section.
5. Make sure to add a meaningful `Description` to the parameter. **This is extremely important to give context** to anyone in need of making
   changes to parameters, so take some time to think about a good, meaningful description.
6. Choose the tier that fits better for this parameter:
   1. If the parameter is small and is not expected to grow much as time passes, choose `Standard`.
   2. On the other hand, if the parameter is large enough and is expected to grow, choose `Advanced`.
7. Choose the type that fits better for this parameter:
   1. If the parameter is safe to stay unencrypted in AWS:
      1. Choose `String`.
      2. Set the `Data Type` field to `text`.
   2. On the other hand, if the parameter needs to be encrypted (see the [Encryption](#encryption) section):
      1. Choose `SecureString`.
      2. Set the `KMS Key Source` field to `My current account` to pick a KMS key registered in the current account.
      3. Set the `KMS Key ID` field to `alias/aws/ssm` to pick the default KMS key for Parameter Store.
   > In general, avoid using `StringList` parameters. These are special cases of the `String` type, which essentially means
   > that `String` can be used to create parameters based on comma-separated values as well.
8. Give the parameter a value that adheres to the conventions specified in the [Values](#values) section.
9. Finally, hit `Create parameter` to save it.

## About the different environments

When creating a new parameter in Parameter Store, please do make sure to create two parameters out of it: one
for `dev` environments, and another one for `pro`. In general, `dev` and `pro` versions of the same parameter will share the same value,
unless there is a strong reason to keep them different.

For example, parameters used to point to third party systems may differ if their app has not only a Production system,
but also a Development / Test one. In that case, the `pro` version of the parameter should aim at the third party's Production system,
and the `dev` version should aim at their Development / Test system.

# Hooking AWS Parameter Store with Kubernetes clusters

## Pre-requisites

Before moving on, make sure to install [k9s](https://github.com/derailed/k9s) in your system. `k9s` is a powerful terminal UI
that lets users manage Kubernetes clusters from their own machines, and even edit Kubernetes objects in place to reflect those changes
immediately.

After installing `k9s`, follow these steps to install a plugin that allows editing decoded `Secret` objects (more in the next section):
1. Install [krew](https://github.com/kubernetes-sigs/krew#installation), following the instructions for the desired OS.
2. Install `kubectl`'s plugin [kubectl-modify-secret](https://github.com/rajatjindal/kubectl-modify-secret#installing), following
   the instructions for the desired OS.
3. Integrate `kubectl-modify-secret` into `k9s`'s plugin system:
   1. In a terminal, run `k9s info` to check which folder holds `k9s` configurations.
   2. Create file `plugin.yml` under that folder, if it does not exist yet.
   3. Add the following snippet:
      ```yaml
      plugin:
        edit-secret:
          shortCut: Ctrl-X
          confirm: false
          description: "Edit Decoded Secret"
          scopes:
            - secrets
          command: kubectl
          background: false
          args:
            - modify-secret
            - --namespace
            - $NAMESPACE
            - --context
            - $CONTEXT
            - $NAME
      ```
      > By default, the shortcut to edit decoded secrets is set to `Ctrl`+`X`. If needed, set a custom one instead.

## Kubernetes: Secrets and ConfigMaps

`Secret` and `ConfigMap` objects are the Kubernetes objects used to inject environment variables to one or multiple pods.
Like other Kubernetes objects, they are defined through `.yaml` files.

These objects hold mappings between environment variables and their values, along with some metadata.

Here is an example of a `ConfigMap` definition:
```yaml
apiVersion: v1
data:
  CURRENT_ENVIRONMENT: production
  ENVIRONMENT_NAME: production
  REDIS_HOSTNAME: redis.pro.somewhere.com
kind: ConfigMap
metadata:
  annotations:
    meta.helm.sh/release-name: automation-engine
    meta.helm.sh/release-namespace: automation-engine
    reloader.stakater.com/match: "true"
  creationTimestamp: "2021-08-30T15:08:12Z"
  labels:
    app.kubernetes.io/instance: automation-engine
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: some-fancy-bridge
    app.kubernetes.io/version: 1.16.0
    component: some-fancy-bridge
    current-environment: production
    environment-name: production
    helm.sh/chart: some-fancy-bridge-0.1.0
    microservice-type: case-of-use
    project: mettel-automation
  name: some-fancy-bridge-configmap
  namespace: automation-engine
  resourceVersion: "83171937"
  selfLink: /api/v1/namespaces/automation-engine/configmaps/some-fancy-bridge-configmap
  uid: ba625451-8ba4-4ac7-a8da-593cc938eae7
```

And here is an example of a `Secret` definition:
```yaml
apiVersion: v1
data:
  THIRD_PARTY_API_USERNAME: aGVsbG8K
  THIRD_PARTY_API_PASSWORD: d29ybGQK
kind: Secret
metadata:
  annotations:
    meta.helm.sh/release-name: automation-engine
    meta.helm.sh/release-namespace: automation-engine
    reconcile.external-secrets.io/data-hash: 3162fd065a6777587e9a3a604e0c56e2
    reloader.stakater.com/match: "true"
  creationTimestamp: "2022-03-08T18:31:36Z"
  labels:
    app.kubernetes.io/instance: automation-engine
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: some-fancy-bridge
    app.kubernetes.io/version: 1.16.0
    component: some-fancy-bridge
    current-environment: production
    environment-name: production
    helm.sh/chart: some-fancy-bridge-0.1.0
    microservice-type: capability
    project: mettel-automation
  name: some-fancy-bridge-secret
  namespace: automation-engine
  ownerReferences:
  - apiVersion: external-secrets.io/v1alpha1
    blockOwnerDeletion: true
    controller: true
    kind: ExternalSecret
    name: some-fancy-bridge-secret
    uid: 42bdad1c-37c4-4890-b86b-d9623333df18
  resourceVersion: "82588568"
  selfLink: /api/v1/namespaces/automation-engine/secrets/some-fancy-bridge-secret
  uid: 81ad3356-8696-406e-bba0-c4ec389676ee
type: Opaque
```

Both objects have a `data` field where the different configurations are stored. The main difference between both objects
is that all fields under `data` remain clear in `ConfigMap` objects, but in `Secret` ones, these fields are base64-encoded.

These objects lack of mechanisms to pull configurations from external sources, so an additional tool is needed to hook them
with AWS Parameter Store.

## External secrets

The (External Secrets Operator)[https://github.com/external-secrets/external-secrets] is a tool that allows setting up `Secret`
objects based on external references through a new kind of object called `ExternalSecret`.

`ExternalSecret` objects define the external source to pull configurations from, and the references that should be resolved. After
these references have been resolved, the `ExternalSecret` will create a regular `Secret` object with a `data` section whose key-value pairs
are based on the environment variables the pod expects to see, and the values gotten after resolving the references from the external
source.

Aside from that, `ExternalSecret` objects pull configuration values from the external source periodically to keep secrets up to date,
also known as _reconciling secrets_.

An example of `ExternalSecret` object would be this one:
```yaml
apiVersion: external-secrets.io/v1alpha1
kind: ExternalSecret
metadata:
  annotations:
    meta.helm.sh/release-name: automation-engine
    meta.helm.sh/release-namespace: automation-engine
    reloader.stakater.com/match: "true"
  creationTimestamp: "2022-03-08T18:11:02Z"
  generation: 1
  labels:
    app.kubernetes.io/instance: automation-engine
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: some-fancy-bridge
    app.kubernetes.io/version: 1.16.0
    component: some-fancy-bridge
    current-environment: production
    environment-name: production
    helm.sh/chart: some-fancy-bridge-0.1.0
    microservice-type: capability
    project: mettel-automation
  name: some-fancy-bridge-secret
  namespace: automation-engine
  resourceVersion: "83201847"
  selfLink: /apis/external-secrets.io/v1alpha1/namespaces/automation-engine/externalsecrets/some-fancy-bridge-secret
  uid: ca5c1faf-1b76-4f59-b57f-e10e43154ace
spec:
  data:
  - remoteRef:
      key: /automation-engine/pro/some-fancy-bridge/third-party-api-username
    secretKey: THIRD_PARTY_API_USERNAME
  - remoteRef:
      key: /automation-engine/pro/some-fancy-bridge/third-party-api-password
    secretKey: THIRD_PARTY_API_PASSWORD
status:
  conditions:
  - lastTransitionTime: "2022-03-08T18:11:10Z"
    message: Secret was synced
    reason: SecretSynced
    status: "True"
    type: Ready
  refreshTime: "2022-03-10T13:29:12Z"
  syncedResourceVersion: 1-3efb62db37d8b935be922ecc6f7ed99f
```

In this example, there are two items under the `data` section. Each item refers to an external / remote reference (field `remoteRef::key`),
and the environment variable that the value behind that remote reference should be loaded to (field `secretKey`).

## Manipulating external secrets in the Automation system

To add, remove, or update external secrets for a particular service in the Automation system, head to
`helm/charts/automation-engine/<service>/templates/external-secret.yaml` and make the appropriate changes under the `data`
section.

For example, consider the following `external-secret.yaml`:
```yaml
{{- if and .Values.global.externalSecrets.enabled -}}
apiVersion: external-secrets.io/v1alpha1
kind: ExternalSecret
metadata:
  name: {{ include "some-fancy-bridge.secretName" . }}
  labels:
    {{- include "some-fancy-bridge.labels" . | nindent 4 }}
  annotations:
    reloader.stakater.com/match: "true"
spec:
  secretStoreRef:
    name: {{ .Values.global.environment }}-parameter-store
    kind: SecretStore 
  target:
    creationPolicy: 'Owner'
   Valid time units are "ns", "us" (or "µs"), "ms", "s", "m", "h" (from time.ParseDuration)
   May be set to zero to fetch and create it 
  {{- if eq .Values.global.current_environment "dev" }}
  refreshInterval: "0"
  {{ else }}
  refreshInterval: "5m"  
  {{- end }}
  data:
    {{- with .Values.global.externalSecrets.envPath }}
    - remoteRef:
        key: {{ . }}/some-fancy-bridge/third-party-api-username
      secretKey: THIRD_PARTY_API_USERNAME
    - remoteRef:
        key: {{ . }}/some-fancy-bridge/third-party-api-password
      secretKey: THIRD_PARTY_API_PASSWORD
    {{- end }}
{{- end }}
```

If a new configuration called `THIRD_PARTY_API_URL` must be added to the underlying `Secret` created by this `ExternalSecret`, a new item should be
placed under the `data` section, and it should look like this:
```yaml
- remoteRef:
    key: {{ . }}/some-fancy-bridge/third-party-api-url
  secretKey: THIRD_PARTY_API_URL
```

The change can then be deployed to the Kubernetes cluster.

### A word of caution about ephemeral environments

Although `external-secrets` is part of the EKS cluster for production and the cluster for
ephemeral environments, the truth is it behaves differently across contexts.

In the production cluster, `ExternalSecret` objects are configured to pull configurations from AWS Parameter Store
every `5 minutes`. That way, if a developer adds, removes, or updated a parameter in AWS, the cluster will realize about
that event to update the regular `Secret` object created by the `ExternalSecret` with the most recent value. This will trigger
another piece in the cluster called [reloader](https://github.com/stakater/Reloader), which ultimately will kill any pod
that relies on the updated secret to spin up a new one with the configurations in the updated `Secret`.

In ephemeral environments however, this is completely different. The `ExternalSecret` object will create a `Secret` object
only when the ephemeral environment is deployed for the first time. After it has been deployed, control and management of
`Secret` objects is delegated to developers; that is, `external-secrets` will never pull parameters from AWS again.

The reasoning behind this behavior is that these parameters are shared by all ephemeral environments, so if one of them were
to be updated in AWS and the polling rate was set to `5 minutes`, all ephemeral environments would be updated because they all share
the same reference. So essentially, the set of configurations for ephemeral environments that are stored in AWS are used as a template
to populate `ExternalSecret` and `Secret` objects in ephemeral environments. If a secret needs to be updated, `k9s` should be used
to edit the `Secret` in place.