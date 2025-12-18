# A/B Variant Deployment Guide

Deploy Bank of Splunk to two namespaces (`a-variant` and `b-variant`) with Splunk OTel Collector auto-instrumentation.

## Prerequisites

- Kubernetes cluster with kubectl configured. Use the [Terraform scripts](https://github.com/splunk/o11y-field-demos/tree/main/k3d-ec2-instance) to set up a `k3d` cluster if needed.

## Step 1: Create Namespaces

```bash
kubectl create namespace a-variant
kubectl create namespace b-variant
```

## Step 2: Deploy Splunk OTel Collector with Auto-Instrumentation

- The Splunk OTel Collector **must be deployed in the `default` namespace** as the `deployment.yaml` references `default/splunk-otel-collector` for auto-instrumentation annotations.
- Export `INDEX` to be either `o11y-demo-us` or `o11y-demo-eu` based on your realm.

```bash
helm repo add splunk-otel-collector-chart https://signalfx.github.io/splunk-otel-collector-chart && helm repo update
```

```bash
export INDEX="o11y-demo-us" # or "o11y-demo-eu"
```

```bash
helm install splunk-otel-collector \
--set="operatorcrds.install=true", \
--set="operator.enabled=true", \
--set="splunkObservability.realm=$REALM" \
--set="splunkObservability.accessToken=$ACCESS_TOKEN" \
--set="clusterName=$INSTANCE-k3s-cluster" \
--set="splunkObservability.profilingEnabled=true" \
--set="agent.service.enabled=true"  \
--set="environment=$INSTANCE" \
--set="splunkPlatform.endpoint=$HEC_URL" \
--set="splunkPlatform.token=$HEC_TOKEN" \
--set="splunkPlatform.index=$INDEX" \
splunk-otel-collector-chart/splunk-otel-collector \
-f ~/otel-collector.yaml
```

## Step 3: Deploy Workshop Secrets to Each Namespace

Apply the workshop secrets to both namespaces:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: workshop-secret
type: Opaque
stringData:
  realm: eu0
  rum_token: xxx
```

```bash
kubectl apply -f workshop-secrets.yaml -n a-variant
kubectl apply -f workshop-secrets.yaml -n b-variant
```

## Step 4: Deploy Application to Both Namespaces

```bash
kubectl apply -f deployment.yaml -n a-variant
kubectl apply -f deployment.yaml -n b-variant
```

## Step 5: Generate New JWT Keys for b-variant

To ensure the b-variant namespace uses unique JWT keys, use the `generate-jwt-keys.sh` script:

```bash
./generate-jwt-keys.sh
```

### Script Contents

The script performs the following operations:

```bash
#!/bin/sh
openssl genrsa -out jwtRS256.key 6120
openssl rsa -in jwtRS256.key -outform PEM -pubout -out jwtRS256.key.pub
kubectl delete secret jwt-key -n b-variant
kubectl create secret generic jwt-key --from-file=./jwtRS256.key --from-file=./jwtRS256.key.pub -n b-variant
kubectl rollout restart deployment -n b-variant
```

This generates a new RSA key pair, creates a Kubernetes secret in the b-variant namespace, and restarts all deployments to pick up the new keys.

## Verification

Check deployments in both namespaces:

```bash
kubectl get pods -n a-variant
kubectl get pods -n b-variant
```

## Cleanup

```bash
kubectl delete namespace a-variant
kubectl delete namespace b-variant
```
