import json
import os
from datetime import datetime
from pprint import pprint

import requests


def get_gist(gist_id=os.environ.get("GITHUB_GIST_ID", "b86d83d7b11377fb4a143d9cb12aef64")):
    """Get a gist with a file named "items.json" from GitHub."""
    print("Getting Item Cache from Gist:", gist_id)
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }

    if os.environ.get("GITHUB_TOKEN"):  # this should make fetching private gists possible
        headers['Authorization'] = f'Bearer {os.environ.get("GITHUB_TOKEN")}'
    return json.loads(requests.get(f'https://api.github.com/gists/{gist_id}', headers=headers).json()["files"]["items.json"]["content"])


def update_gist(item_cache: dict, gist_id=os.environ.get("GITHUB_GIST_ID", "b86d83d7b11377fb4a143d9cb12aef64")):
    """Update the gist with a file named "items.json" on GitHub."""
    if not os.environ.get("GITHUB_TOKEN"):
        print("No GitHub Token found, skipping updating online item cache.")
        return
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {os.environ.get("GITHUB_TOKEN")}',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    content = json.dumps(item_cache, sort_keys=True,indent=2).replace('"', '\\"').replace("\n", "\\n")
    data = f'{{"description":"Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}","files":{{"items.json":{{"content":"{content}"}}}}}}'
    response = requests.patch(f'https://api.github.com/gists/{gist_id}', headers=headers, data=data)
    if response.status_code == 200:
        print("Successfully updated Gist.")
    else:
        print("Failed to update Gist:", response.text)

