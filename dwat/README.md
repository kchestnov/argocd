# dwat.py

Dashboard WATcher - Simple python to diff between existing grafana dashboards and a git repo (github in a first iteration)
Will open PR if there is a difference

Does not perform backward-compatibility e.g. 
* Dashboards that are in Git-repo but not in Grafana instance
* Dashboards that are deleted from Grafana instance

## Usage
* source env.sh - configures your enviroment with correct packages
* .env - python-specific config for env variables, you need to create one with the following content
    ``` python
    # Grafana Configuration
    GRAFANA_API_URL = "http://127.0.0.1:3001/api"
    GRAFANA_API_TOKEN = "your-token"

    # GitHub Configuration
    GITHUB_TOKEN = "your-token"
    GITHUB_REPO_NAME = "kchestnov/argocd-examples-kchestnov"
    FOLDER_NAME = "helm-chart-grafana-crd"
    FILE_NAME = "values.yaml"
    BRANCH_PREFIX = "update-dashboard-"
    TIMEOUT = "30"
    ```

* `python dwat.py` to run the program once