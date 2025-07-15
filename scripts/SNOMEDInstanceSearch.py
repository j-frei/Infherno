from typing import List

import sys
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

if __name__ == "__main__":
    # get arg parser arguments
    import argparse
    parser = argparse.ArgumentParser(description="Get latest branches of a Snowstorm instance")
    parser.add_argument("given_url", type=str, nargs='?', default="https://browser.ihtsdotools.org", help="URL of a Snowstorm or Snomed instance")
    args = parser.parse_args()

    given_url = args.given_url
    snowstorm_url = to_snowstorm(given_url)

    if snowstorm_url is not None:
        print(f"Given URL: {given_url}")
        print(f"Snowstorm URL: {snowstorm_url}")
        branches = getLatestBranches(snowstorm_url)
        print("Branches:")
        for branch in branches:
            print(f" - [{repr(branch['branch'])}] {branch['name']}")
    else:
        print(f"URL is not a Snowstorm or Snomed instance: {given_url}")