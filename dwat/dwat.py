# pylint: disable=missing-module-docstring
import os
import json
import requests
import yaml
from github import Github
from dotenv import load_dotenv

load_dotenv()

# Configuration
GRAFANA_API_URL = os.getenv("GRAFANA_API_URL")
GRAFANA_API_TOKEN = os.getenv("GRAFANA_API_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME")
FOLDER_NAME = os.getenv("FOLDER_NAME")
FILE_NAME = os.getenv("FILE_NAME", "values.yaml")
VALUES_YAML = f"{FOLDER_NAME}/{FILE_NAME}"
HELM_CHART_ROOT_KEY = "dashboards"
BRANCH_PREFIX = os.getenv("BRANCH_PREFIX", "update-dashboard-")
TIMEOUT = int(os.getenv("TIMEOUT", "30"))

HEADERS = {
    "Authorization": f"Bearer {GRAFANA_API_TOKEN}",
    "Content-Type": "application/json",
}

# TODO: Add proper logging
# TODO: Add Prometheus metrics
# TODO: Run in a main loop every "DURATION" seconds
# TODO: Check if it works with nested helm-charts
# TODO: Add more reliability: catch already created branches, update PRs
# TODO: Catch non-existing files/folders etc gracefully, do not attempt to modify what does not belong to us
# TODO: Add link to source dashboard into PR, Add link to a "future" dashboard in PR


def fetch_dashboards_from_grafana() -> dict:
    """
    Search folders and dashboards

    https://grafana.com/docs/grafana/latest/developers/http_api/folder_dashboard_search/

    Args:
        GRAFANA_API_URL (str): The grafana instance
        GRAFANA_API_TOKEN (str): The API Token with sufficient permissions
        TIMEOUT (int): Timeout value for HTTP request

    Returns:
        list: Converted response of the query containing only "dash-db" entries
        {"fe50gkfjmzmrkf": {<response.json entry>}}

    Examples:

        response.json() = [{
            "id": 469,
            "uid": "de50nm7qz9f5sf",
            "title": "sync-folder",
            "uri": "db/sync-folder",
            "url": "/dashboards/f/de50nm7qz9f5sf/sync-folder",
            "slug": "",
            "type": "dash-folder",
            "tags": [],
            "isStarred": False,
            "sortMeta": 0
        }, {
            "id": 468,
            "uid": "fe50gkfjmzmrkf",
            "title": "dashboard-1",
            "uri": "db/dashboard-1",
            "url": "/d/fe50gkfjmzmrkf/dashboard-1",
            "slug": "",
            "type": "dash-db",
            "tags": [],
            "isStarred": False,
            "folderId": 469,
            "folderUid": "de50nm7qz9f5sf",
            "folderTitle": "sync-folder",
            "folderUrl": "/dashboards/f/de50nm7qz9f5sf/sync-folder",
            "sortMeta": 0
        }]

    """

    try:
        response = requests.get(
            f"{GRAFANA_API_URL}/search", headers=HEADERS, timeout=TIMEOUT
        )
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching dashboards from Grafana: {e}")
        return {}

    result = {}
    for dashboard in response.json():
        if not dashboard["uid"]:
            continue
        # Filter dash-folders
        if dashboard["type"] == "dash-folder":
            continue
        # Do not sync dashboards without tags
        if not dashboard["tags"]:
            continue
        result[dashboard["uid"]] = dashboard
    return result


def fetch_dashboard_details_from_grafana(uid: str) -> dict:
    """
    Get dashboard by uid

    https://grafana.com/docs/grafana/latest/developers/http_api/dashboard/

    Args:
        GRAFANA_API_URL (str): The grafana instance
        GRAFANA_API_TOKEN (str): The API Token with sufficient permissions
        TIMEOUT (int): Timeout value for HTTP request
        uid (str): uid of a dashboard

    Returns:
        dict: Converted response of a query

    """

    try:
        response = requests.get(
            f"{GRAFANA_API_URL}/dashboards/uid/{uid}", headers=HEADERS, timeout=TIMEOUT
        )
        response.raise_for_status()
        dashboard_model = response.json()
        return dashboard_model.get("dashboard", {})
    except requests.exceptions.RequestException as e:
        print(f"Error fetching model for dashboard UID {uid}: {e}")
        return {}


def fetch_dashboards_from_github() -> dict:
    """
    Get dashboards from github repo

    Args:
        GITHUB_REPO_NAME (str): Repository name in GitHub
        GITHUB_TOKEN (str): API Token with sufficient permissions
        VALUES_YAML (str): Full path inside repo to values.yaml
        HELM_CHART_ROOT_KEY (str): top-level values.yaml key, we return everything UNDER it
        TIMEOUT (int): Timeout value for HTTP request

    Returns:
        dict: Converted content of the values.yaml

    Example:

    VALUES_YAML

    dashboards:
        fe50gkfjmzmrkf:
            title: "dashboard-1"
            tags: ['v0.0.1']
            folder_uid: de50nm7qz9f5sf
            folder_title: sync-folder
            json: '{"annotations": {"list": [{"builtIn": 1, "datasource": {"type": "grafana",
                    "uid": "-- Grafana --"}, "enable": true, "hide": true, "iconColor": "rgba(0,
                    211, 255, 1)", "name": "Annotations & Alerts", "type": "dashboard"}]}, "editable":
                    true, "fiscalYearStartMonth": 0, "graphTooltip": 0, "id": 468, "links":
                    [], "panels": [{"datasource": {"type": "datasource", "uid": "grafana"},
                    "fieldConfig": {"defaults": {"color": {"mode": "palette-classic"}, "custom":
                    {"axisBorderShow": false, "axisCenteredZero": false, "axisColorMode": "text",
                    "axisLabel": "", "axisPlacement": "auto", "barAlignment": 0, "drawStyle":
                    "line", "fillOpacity": 0, "gradientMode": "none", "hideFrom": {"legend":
                    false, "tooltip": false, "viz": false}, "insertNulls": false, "lineInterpolation":
                    "linear", "lineWidth": 1, "pointSize": 5, "scaleDistribution": {"type":
                    "linear"}, "showPoints": "auto", "spanNulls": false, "stacking": {"group":
                    "A", "mode": "none"}, "thresholdsStyle": {"mode": "off"}}, "mappings": [],
                    "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value":
                    null}, {"color": "red", "value": 80}]}}, "overrides": []}, "gridPos": {"h":
                    8, "w": 12, "x": 0, "y": 0}, "id": 1, "options": {"legend": {"calcs": [],
                    "displayMode": "list", "placement": "bottom", "showLegend": true}, "tooltip":
                    {"mode": "single", "sort": "none"}}, "title": "Panel Title", "type": "timeseries"}],
                    "schemaVersion": 39, "tags": [], "templating": {"list": []}, "time": {"from":
                    "now-6h", "to": "now"}, "timepicker": {}, "timezone": "browser", "title":
                    "dashboard-1", "uid": "fe50gkfjmzmrkf", "version": 2, "weekStart":
                    ""}'

    """
    # TODO: Write better try-except
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO_NAME)
        content_file = repo.get_contents(VALUES_YAML)
        # Dashboard JSON structure is a string here
        github_dashboards = yaml.safe_load(content_file.decoded_content.decode())
        return github_dashboards

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error fetching dashboards from GitHub: {e}")
        return {}


def compare_dashboards(grafana_dashboards: dict, github_dashboards: dict) -> list:
    """
    Validate if grafana_dashboards are present in Github

    Does not perform backward check
    e.g. does not return dashboards from github that are not in grafana

    Args:
        grafana_dashboards (dict): Response of fetch_dashboards_from_grafana
        fetch_dashboards_from_github (dict): Response of fetch_dashboards_from_github

    Returns:
        list: List of grafana dashboards that are not yet present in Github
        [(reason, {dashboard})]

    """

    missing_or_different = []

    for grafana_dashboard in grafana_dashboards:

        uid = grafana_dashboard
        tags = grafana_dashboards[uid]["tags"]

        github_dashboard = github_dashboards.get(uid, "")

        reason = ""
        if github_dashboard == "":
            reason = "Not found in GitHub"

        elif tags != github_dashboard["tags"]:
            reason = "Different from GitHub"

        if reason:
            grafana_model = fetch_dashboard_details_from_grafana(uid)
            # Dashboard does not exist, creating new structure
            missing_or_different.append(
                (
                    reason,
                    {
                        uid: {
                            "title": grafana_dashboards[uid].get("title"),
                            "tags": tags,
                            "folder_uid": grafana_dashboards[uid].get(
                                "folderUid", "general"
                            ),
                            "folder_title": grafana_dashboards[uid].get(
                                "folderTitle", "General"
                            ),
                            "json": json.dumps(grafana_model),
                        }
                    },
                )
            )

    return missing_or_different


def merge_dashboard(dashboard, dashboards):
    """
    Inserts in-place dashboard dict into dict of dashboards

    Args:
        dashboard (dict): Dashboard details
        dashboards (dict): Dictionary of dashboards fetched from values.yaml
    """
    dashboards.update(dashboard)


def create_pr(repo: object, reason: str, dashboard: dict, dashboards: dict):
    """
    Creates PR to provided Repo

    Args:
        repo (int): Git repository to open PR
        reason (str): Short message for commit and PR
        dashboard (dict): Additional details about dashboard that is being updated
        dashboards (dict): Content of a file
        BRANCH_PREFIX (str): PR will be opened from a branch prefixed with this
        VALUES_YAML (str): Location of a file
    """
    # TODO: Maybe drop dashboard dict completelly and leave only message
    uid, dashboard = next(iter(dashboard.items()))
    branch_name = f"{BRANCH_PREFIX}{uid}"
    commit_message = f'{reason}: Update dashboard {dashboard["title"]} in {dashboard["folder_title"]}'
    pr_title = f'{reason}: {dashboard["title"]}'

    # Create a new branch
    # TODO: check if branch exists already, and add commit there instead
    # github.GithubException.GithubException: 422 {"message": "Reference already exists", "documentation_url": "https://docs.github.com/rest/git/refs#create-a-reference", "status": "422"}

    main_ref = repo.get_branch("main")
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_ref.commit.sha)

    # Add or update the dashboard file
    # TODO: check if file exists here
    contents = repo.get_contents(VALUES_YAML, ref="main")
    repo.update_file(
        path=VALUES_YAML,
        message=commit_message,
        content=yaml.dump(dashboards),
        sha=contents.sha,
        branch=branch_name,
    )

    # Open a PR
    # TODO: if PR already there, update it
    # TODO: revert (remove branch e.g. if we fail here)
    pr = repo.create_pull(
        title=pr_title,
        body=f'This PR {reason.lower()} the Grafana dashboard `{dashboard["title"]}` (UID: `{uid}`).',
        head=branch_name,
        base="main",
    )
    print(f"PR created: {pr.html_url}")


def main():
    # pylint: disable=missing-docstring
    grafana_dashboards = fetch_dashboards_from_grafana()
    github_dashboards = fetch_dashboards_from_github()
    missing_or_different = compare_dashboards(
        grafana_dashboards, github_dashboards[HELM_CHART_ROOT_KEY]
    )

    if not missing_or_different:
        print("All dashboards in Grafana are up-to-date on GitHub.")
        return

    print("Creating Pull Requests for missing or different dashboards...")

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO_NAME)

    for reason, dashboard in missing_or_different:

        new_values_yaml = github_dashboards.copy()
        merge_dashboard(dashboard, new_values_yaml[HELM_CHART_ROOT_KEY])
        create_pr(repo, reason, dashboard, new_values_yaml)


if __name__ == "__main__":
    main()
