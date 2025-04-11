import requests
from datetime import datetime, timedelta
from urllib.parse import quote
import argparse
import os

# === CONFIG ===
GITLAB_URL = os.getenv("GITLAB_URL")
API_URL = f"{GITLAB_URL}/api/v4"
PRIVATE_TOKEN = os.getenv("GITLAB_TOKEN")
DATE_FROM = (datetime.now() - timedelta(days=30)).isoformat()  # Past month
# make these empty arrays if you want all projects
GROUP_IDS = [9, 17]
PROJECT_IDS = [49, 57, 55]

HEADERS = {
    "PRIVATE-TOKEN": PRIVATE_TOKEN
}

def get_standalone_projects(project_ids):
    projects = []
    for pid in project_ids:
        url = f"{API_URL}/projects/{pid}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            print(f"Warning: Couldn't fetch project {pid} – {resp.text}")
            continue
        data = resp.json()
        projects.append({
            "id": data["id"],
            "name": data["name_with_namespace"]
        })
    return projects

def get_all_projects():
    projects = []
    page = 1
    while True:
        url = f"{API_URL}/projects?per_page=100&page={page}&simple=true"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            raise Exception(f"Failed to fetch all projects: {resp.text}")
        data = resp.json()
        if not data:
            break
        projects.extend(data)
        page += 1
    return [{"id": p["id"], "name": p["name_with_namespace"]} for p in projects]

def get_projects_in_group(group_id):
    projects = []
    page = 1
    while True:
        url = f"{API_URL}/groups/{quote(str(group_id))}/projects?include_subgroups=true&per_page=100&page={page}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            raise Exception(f"Failed to fetch projects: {resp.text}")
        data = resp.json()
        if not data:
            break
        projects.extend(data)
        page += 1
    # Return a list of dicts with ID and name
    return [{"id": p["id"], "name": p["name_with_namespace"]} for p in projects]

def get_pipelines(project_id, date_from):
    pipelines = []
    page = 1
    while True:
        url = f"{API_URL}/projects/{project_id}/pipelines?updated_after={date_from}&per_page=100&page={page}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            break
        data = resp.json()
        if not data:
            break
        pipelines.extend(data)
        page += 1
    return pipelines


def get_jobs(project_id, pipeline_id):
    url = f"{API_URL}/projects/{project_id}/pipelines/{pipeline_id}/jobs"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        return []
    return resp.json()

def calculate_ci_minutes(projects, date_from):
    report = []
    print(f"Calculating CI minutes for {len(projects)} projects...")
    for project in projects:
        print(".", end="", flush=True)
        project_id = project["id"]
        project_name = project["name"]
        total_seconds = 0
        pipelines = get_pipelines(project_id, date_from)
        for pipeline in pipelines:
            jobs = get_jobs(project_id, pipeline["id"])
            for job in jobs:
                if job["status"] == "success" and job.get("duration"):
                    total_seconds += job["duration"]
        total_minutes = round(total_seconds / 60, 2)
        report.append({
            "project_id": project_id,
            "project_name": project_name,
            "ci_minutes_used": total_minutes
        })
    print()
    return report

def main(days: int = 30, group_ids: list[int] = [], project_ids: list[int] = []):
    projects = []
    if group_ids:
        print("Fetching projects from groups...")
        for group_id in group_ids:
            projects += get_projects_in_group(group_id)

    if project_ids:
        print("Fetching standalone projects...")
        projects += get_standalone_projects(project_ids)

    if not projects:
        print("No group or standalone IDs specified. Fetching all accessible projects...")
        projects = get_all_projects()

    print(f"Found {len(projects)} projects.")
    date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    report = calculate_ci_minutes(projects, date_from)
    total_ci_minutes = sum(entry['ci_minutes_used'] for entry in report)
    print(f"Total CI minutes used in the past {days} days: {total_ci_minutes}")
    print("-" * 80)
    print("Project ID,Project Name,CI Minutes Used")
    for entry in report:
        print(f"{entry['project_id']},{entry['project_name']},{entry['ci_minutes_used']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate CI minutes used by projects")
    parser.add_argument("--days", type=int, default=30, help="Number of days to calculate CI minutes for")
    args = parser.parse_args()
    main(args.days, GROUP_IDS, PROJECT_IDS)
