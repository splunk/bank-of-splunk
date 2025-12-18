#!/bin/sh
openssl genrsa -out jwtRS256.key 5120
openssl rsa -in jwtRS256.key -outform PEM -pubout -out jwtRS256.key.pub
kubectl delete secret jwt-key -n b-variant
kubectl create secret generic jwt-key --from-file=./jwtRS256.key --from-file=./jwtRS256.key.pub -n b-variant
kubectl rollout restart deployment -n b-variant
