
from typing import Optional, TypedDict, List
import requests
from urllib.parse import urljoin, urlparse


def sanitize_url(url: str) -> str:
    return urljoin(url, urlparse(url).path)

def is_snowstorm(url: str) -> bool:
    # Try to query the version endpoint
    version_url = f"{url}/version"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en",
        "User-Agent": "curl/8.0.1", # Yes, Curl User Agent is needed for the public instance!
    }
    try:
        response = requests.get(version_url, headers=headers)
    except requests.exceptions.ConnectionError:
        print("Request yielded a Connection error. You may have been blocked for URL: " + version_url, file=sys.stderr)
        return []
    if response.status_code == 200:
        response_json = response.json()
        if "version" in response_json:
            return True
    return False

def to_snowstorm(url: str) -> str:
    url = sanitize_url(url)

    if is_snowstorm(url):
        return url
    else:
        # Try to add the snowstorm path
        url += "/snowstorm/snomed-ct"
        if is_snowstorm(url):
            return url
        else:
            return None

def getLatestBranches(snowstorm_url: str) -> List[str]:
    branches_url = f"{snowstorm_url}/codesystems"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en",
        "User-Agent": "curl/8.0.1", # Yes, Curl User Agent is needed for public instance!
    }
    try:
        response = requests.get(branches_url, headers=headers)
    except requests.exceptions.ConnectionError:
        print("Request yielded a Connection error. You may have been blocked for URL: " + branches_url, file=sys.stderr)
        return []

    if response.status_code == 200:
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            print("Reponse is not a JSON response. You may have been blocked for URL: " + branches_url, file=sys.stderr)
            return []

        if "items" in response_json:
            return [
                {
                    "name": f"{item['name']} ({item['latestVersion']['version']})" if "name" in item else item["latestVersion"]["branchPath"],
                    "branch": item["latestVersion"]["branchPath"]
                }
                for item in response_json["items"]
                if "latestVersion" in item
            ]

    print("Request was not successful. You may have been blocked for URL: " + branches_url, file=sys.stderr)
    return []
