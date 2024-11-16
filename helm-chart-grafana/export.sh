#!/bin/bash

# Getting pass
kubectl get secret --namespace default kchestnov-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=kchestnov-grafana" -o jsonpath="{.items[0].metadata.name}")
kubectl --namespace default port-forward $POD_NAME 3000:3000 &
