import os
import requests
import datetime

# Use GitHub Actions secret token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

REPO_OWNER = "iamdulanga"
REPO_NAME = "iqair-data-scraper"
BRANCH = "main"
FOLDERS = ["all_stations_maps", "charts"]

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=3)

def get_files(folder):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{folder}?ref={BRANCH}"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else []

def delete_file(file_path, sha):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    response = requests.delete(url, json={"message": f"Delete {file_path}", "sha": sha, "branch": BRANCH}, headers=HEADERS)
    print(f"Deleted: {file_path}" if response.status_code == 200 else f"Failed to delete {file_path}")

def clean_old_files():
    for folder in FOLDERS:
        files = get_files(folder)
        for file in files:
            file_name, file_path, file_sha = file["name"], file["path"], file["sha"]
            try:
                file_date = datetime.datetime.strptime(file_name[:10], "%Y-%m-%d")
                if file_date < cutoff_date:
                    delete_file(file_path, file_sha)
            except ValueError:
                print(f"Skipping: {file_name}")

if __name__ == "__main__":
    clean_old_files()
