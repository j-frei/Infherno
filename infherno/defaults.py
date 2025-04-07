import os

from infherno.tools.fhircodes.utils import (
    getLatestBranches,
    to_snowstorm
)

# Default values for the SNOMED (Snowstorm instance)
SNOWSTORM_URL = None
def determine_snowstorm_url() -> str:
    global SNOWSTORM_URL
    if SNOWSTORM_URL is not None:
        return SNOWSTORM_URL
    else:
        url = os.getenv("SNOWSTORM_URL", "https://browser.ihtsdotools.org")

        # Check if the URL is a valid Snowstorm URL
        snowstorm_url = to_snowstorm(url)
        if snowstorm_url is None:
            raise ValueError(f"URL {url} is not a valid Snowstorm URL")

        SNOWSTORM_URL = snowstorm_url
        return SNOWSTORM_URL

SNOWSTORM_BRANCHES = None
SNOWSTORM_BRANCH = None
def determine_snowstorm_branch(snomed_url: str = None) -> str:
    global SNOWSTORM_BRANCHES
    global SNOWSTORM_BRANCH

    if SNOWSTORM_BRANCH is not None:
        return SNOWSTORM_BRANCH
    else:
        if SNOWSTORM_BRANCHES is None:
            if snomed_url is None:
                snomed_url = determine_snowstorm_url()

            # Read available branched for the Snowstorm instance
            SNOWSTORM_BRANCHES = getLatestBranches(snomed_url)
            given_branch = os.getenv("SNOWSTORM_BRANCH", None)
            # Check if the custom branch is available
            if given_branch is not None:
                found_branches = [item for item in SNOWSTORM_BRANCHES if item["branch"] == given_branch]
                if len(found_branches) == 0:
                    raise ValueError(f"Branch {given_branch} not found in the Snowstorm instance")
                else:
                    SNOWSTORM_BRANCH = given_branch
                    return SNOWSTORM_BRANCH

        if len(SNOWSTORM_BRANCHES) == 0:
            raise ValueError("No branches found for the Snowstorm instance")

        # Use the first branch as default
        SNOWSTORM_BRANCH = SNOWSTORM_BRANCHES[0]["branch"]
        return SNOWSTORM_BRANCH
