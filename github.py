import json
import os
import time
from datetime import datetime

import requests


def get_gist(gist_id=os.environ.get("GITHUB_GIST_ID", "b86d83d7b11377fb4a143d9cb12aef64")):
    """Get a gist with a file named "items.json" from GitHub."""
    print("Getting Item Cache from Gist:", gist_id)
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }

    if os.environ.get("GITHUB_GIST_TOKEN"):  # this should make fetching private gists possible
        headers['Authorization'] = f'Bearer {os.environ.get("GITHUB_GIST_TOKEN")}'

    attempt = 0
    max_attempts = 5
    response = None
    while attempt < max_attempts:
        try:
            response = requests.get(f'https://api.github.com/gists/{gist_id}', headers=headers)
            # If the request was successful, break out of the loop
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            attempt += 1
            print(f"Attempt {attempt} failed, retrying in 3 seconds...")
            if attempt == max_attempts:
                # Raise the exception if the maximum number of attempts has been reached
                raise e
            # Wait before retrying
            time.sleep(3)

    if response is not None:
        print("Successfully fetched Item Cache Gist.")
        return json.loads(response.json()["files"]["items.json"]["content"])
    else:
        print("Failed to fetch Item Cache Gist.")
        return {}


def update_gist(item_cache: dict, gist_id=os.environ.get("GITHUB_GIST_ID", "b86d83d7b11377fb4a143d9cb12aef64")) -> str:
    """Update the gist with a file named "items.json" on GitHub."""
    if not os.environ.get("GITHUB_GIST_TOKEN"):
        print("No GitHub Token found, skipping updating online item cache.")
        return "The item cache was updated. *Gist was not updated, because no GitHub Token was found.*"

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {os.environ.get("GITHUB_GIST_TOKEN")}',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    content = json.dumps(item_cache, sort_keys=True, indent=2).replace('"', '\\"').replace("\n", "\\n")
    data = f'{{"description":"Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}","files":{{"items.json":{{"content":"{content}"}}}}}}'
    response = requests.patch(f'https://api.github.com/gists/{gist_id}', headers=headers, data=data)
    if response.status_code == 200:
        print("Successfully updated Item Cache Gist.")
        return "The item cache was updated. Gist was updated successfully."
    else:
        print("Failed to update Item Cache Gist:", response.text)
        return f"The item cache was updated. **Gist was not updated, because the update failed:** `{response.text}`"
