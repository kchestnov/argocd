# This is a placeholder if a helm chart

Installation is not complex, just follow

* kubectl create namespace argocd
* kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
* curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
* sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd