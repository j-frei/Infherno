import sys
from typing import Optional, TypedDict, List
import requests, urllib

class ConceptItemMatch(TypedDict):
    id: str
    term: str

def getECLfromConceptRoots(concept_root_ids: List[str]) -> str:
    """Builds an ECL query from a list of concept root IDs."""
    return " or ".join([ f"<< {cri.strip()}" for cri in concept_root_ids if cri.strip() ])

class GenericSnomedInstance:
    def __init__(self,
        base_url: str = "https://snowstorm.ihtsdotools.org/snowstorm/snomed-ct",
        branch: str = "MAIN/2023-09-01",
        branch_encode: bool = True,
        get_only: bool = True,
    ):
        self.base_url = base_url
        self.branch = urllib.parse.quote_plus(branch) if branch_encode else branch
        self.headers = {
            "Accept": "application/json",
            "Accept-Language": "en",
            "User-Agent": "curl/8.0.1", # Yes, Curl User Agent is needed for public instance!
        }
        self.get_only = get_only

    def search_by_concepts(
        self,
        term: Optional[str] = None,
        ecl: Optional[str] = None,
        conceptIds: Optional[List[str]] = None,
        activeFilter: bool = True,
        getRawResponse: bool = False,
        offset: int = 0,
        limit: Optional[int] = 10,
        use_fsn: bool = True
    ) -> List[ConceptItemMatch]:
        """Searches for concepts by term, ECL or concept IDs."""
        if not self.branch:
            raise ValueError("Branch not set.")

        body = [
            ("activeFilter", True if activeFilter else False),
            ("offset", offset)
        ]
        if limit is not None:
            body.append( ("limit", limit) )
        else:
            body.append( ("limit", 10000) )

        if term is not None:
            if self.get_only:
                body.append( ("term", term) )
            else:
                body.append( ("termFilter", term) )

        if conceptIds is not None:
            if self.get_only:
                for conceptId in conceptIds:
                    body.append( ("conceptIds", conceptId) )
            else:
                body.append( ("conceptIds", conceptIds) )

        if ecl is not None:
            if self.get_only:
                body.append( ("ecl", ecl) )
            else:
                body.append( ("eclFilter", ecl) )

        if self.get_only:
            url = f"{self.base_url}/{self.branch}/concepts"
            response = requests.get(url, headers=self.headers, params=body)
        else:
            url = f"{self.base_url}/{self.branch}/concepts/search"
            response = requests.post(url, headers=self.headers, json=body)

        # Check manually for certain errors
        if response.status_code == 400 and response.json().get("message", "")\
            .startswith("Concepts in the ECL request do not exist or are inactive"):
            res = response.json()

            print("Treat request as no concepts found, due to error message:", res["message"], file=sys.stderr)
            if getRawResponse:
                res["total"] = 0
                return res
            else:
                return []

        response.raise_for_status()

        res = response.json()
        if getRawResponse:
            return res

        return [
            {
                "id": item["id"],
                "term": item["fsn" if use_fsn else "pt"]["term"]
            } for item in res.get("items", [])
        ]

    def search_term_by_browse_descriptions(
        self,
        term: Optional[str] = None,
        activeFilter: bool = True,
        semanticTags: Optional[List[str]] = None,
        getRawResponse: bool = False,
        offset: int = 0,
        limit: int = 10,
        use_fsn: bool = True,
    ) -> List[ConceptItemMatch]:
        if not self.branch:
            raise ValueError("Branch not set.")

        params = [
            ("activeFilter", "true" if activeFilter else "false"),
            ("offset", offset),
            ("limit", limit),
        ]

        if term is not None:
            params.append(("term", term))

        if semanticTags is not None:
            if isinstance(semanticTags, str):
                params.append(("semanticTags", semanticTags))
            else:
                for semanticTag in semanticTags:
                    params.append(("semanticTags", semanticTag))

        params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

        url = f"{self.base_url}/browser/{self.branch}/descriptions"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        res = response.json()
        if getRawResponse:
            return res

        concepts = [ item["concept"] for item in res.get("items", []) ]
        return [
            {
                "id": concept["id"],
                "term": concept["fsn" if use_fsn else "pt"]["term"]
            } for concept in concepts
        ]

    def search_term_by_multisearch_descriptions(
        self,
        term: str,
        activeFilter: bool = True,
        getRawResponse: bool = False,
        offset: int = 0,
        limit: int = 10,
        use_fsn: bool = True
    ) -> List[ConceptItemMatch]:

        params = [
            ("activeFilter", "true" if activeFilter else "false"),
            ("offset", offset),
            ("limit", limit),
            ("term", term),
        ]
        params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

        url = f"{self.base_url}/multisearch/descriptions"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        res = response.json()

        if getRawResponse:
            return res

        concepts = [ item["concept"] for item in res.get("items", []) if "concept" in item ]
        return [
            {
                "id": concept["conceptId"],
                "term": concept["fsn" if use_fsn else "pt"]["term"]
            } for concept in concepts
        ]

    def search_term_by_relationship(
        self,
        source: Optional[str] = None,
        type: Optional[str] = None,
        destination: Optional[str] = None,
        activeFilter: bool = True,
        getRawResponse: bool = False,
        offset: int = 0,
        limit: Optional[int] = 10,
        use_fsn: bool = True,
        extract: str = "source", # source, target or all
    ) -> List[ConceptItemMatch]:
        if not self.branch:
            raise ValueError("Branch not set.")

        if extract not in ["source", "target", "all"]:
            raise ValueError("extract must be one of: 'source', 'target', 'all'")

        params = [
            ("activeFilter", "true" if activeFilter else "false"),
            ("offset", offset),
        ]
        if limit is not None:
            params.append(("limit", limit))
        else:
            params.append(("limit", limit))

        if source is not None:
            params.append(("source", source))

        if type is not None:
            params.append(("type", type))
        if destination is not None:
            params.append(("destination", destination))
        params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

        url = f"{self.base_url}/{self.branch}/relationships"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        res = response.json()
        if getRawResponse:
            return res

        result_items = [
            {
                "source": { "id": item["source"]["id"], "term": item["source"]["fsn" if use_fsn else "pt"]["term"] },
                "target": { "id": item["target"]["id"], "term": item["target"]["fsn" if use_fsn else "pt"]["term"] },
            }
            for item in res.get("items", [])
        ]

        if extract != "all":
            result_items = [ item[extract] for item in result_items ]
        return result_items

if __name__ == "__main__":
    import json

    # NHS instance is extremely outdated, does not match REST Swagger format :(
    #print("SNOMED UK NHS instance...")
    #instance_nhs = SnomedInstance("https://termbrowser.nhs.uk/sct-browser-api/snomed", branch="uk-edition/v20230927", branch_encode=False)
    #print(json.dumps(instance_nhs.search_term_by_descriptions("Paracetamol", limit=1), indent=4))
    #print()

    # Test Medication (-> vanilla International (INT) does not have it)
    term="EVICEL"

    # Query vanilla, public international instance for Descriptions
    print("Descriptions | SNOMED INT instance...")
    instance = GenericSnomedInstance("https://snowstorm.ihtsdotools.org/snowstorm/snomed-ct", branch="MAIN/2023-09-01")
    print(json.dumps(instance.search_term_by_browse_descriptions(term, limit=2), indent=4))
    print()

    # Query internal UK instance for Descriptions
    print("Descriptions | SNOMED Internal UK instance (Snowstorm)...")
    instance = GenericSnomedInstance("http://snowstorm-uk.misit-augsburg.de", branch="MAIN/2023-08-30", branch_encode=False)
    print(json.dumps(instance.search_term_by_browse_descriptions(term, limit=2), indent=4))
    print()

    # Query internal UK instance for Descriptions by other API URL
    print("Descriptions | SNOMED Internal UK instance (Snomed)...")
    instance = GenericSnomedInstance("http://snomed-uk.misit-augsburg.de/snowstorm/snomed-ct", branch="MAIN/2023-08-30", branch_encode=False)
    print(json.dumps(instance.search_term_by_browse_descriptions(term, limit=2), indent=4))
    print()

    # Query internal UK instance for Descriptions using MultiSearch
    print("Descriptions MS | SNOMED Internal UK instance (Snowstorm)...")
    instance = GenericSnomedInstance("http://snowstorm-uk.misit-augsburg.de", branch="MAIN/2023-08-30", branch_encode=False)
    print(json.dumps(instance.search_term_by_multisearch_descriptions(term, limit=2), indent=4))
    print()

    # Query internal UK instance for Descriptions using MultiSearch by other API URL
    print("Descriptions MS | SNOMED Internal UK instance (Snomed)...")
    instance = GenericSnomedInstance("http://snomed-uk.misit-augsburg.de/snowstorm/snomed-ct", branch="MAIN/2023-08-30", branch_encode=False)
    print(json.dumps(instance.search_term_by_multisearch_descriptions(term, limit=2), indent=4))
    print()

    # Query vanilla, public international instance for Descriptions using MultiSearch
    print("Descriptions MS | SNOMED INT instance (Snomed)...")
    instance = GenericSnomedInstance("https://snowstorm.ihtsdotools.org/snowstorm/snomed-ct", branch="MAIN/2023-10-01")
    print(json.dumps(instance.search_term_by_multisearch_descriptions(term, limit=2), indent=4))
    print()

    # Query vanilla, public international instance for Concepts
    print("Concepts | SNOMED INT instance...")
    instance = GenericSnomedInstance("https://snowstorm.ihtsdotools.org/snowstorm/snomed-ct", branch="MAIN/2023-10-01")
    print(json.dumps(instance.search_by_concepts(term, limit=2), indent=4))
    print()

    # Query internal UK instance for Concepts
    print("Concepts | SNOMED Internal UK instance (Snowstorm)...")
    instance = GenericSnomedInstance("http://snowstorm-uk.misit-augsburg.de", branch="MAIN/2023-08-30", branch_encode=False)
    print(json.dumps(instance.search_by_concepts(term, limit=2), indent=4))
    print()

    # Try semanticTag filtering
    term="is a"
    tag = ["attribute"]
    print("SemanticTag 'attribute' with 'is a' -> should find 116680003 | SNOMED Internal UK instance (Snowstorm)...")
    instance = GenericSnomedInstance("http://snowstorm-uk.misit-augsburg.de", branch="MAIN/2023-08-30", branch_encode=False)
    print(json.dumps(instance.search_term_by_browse_descriptions(term, limit=2, semanticTags=tag), indent=4))
    print()

    term="is a"
    tag = ["attribute", "substance"]
    print("SemanticTag 'attribute', 'substance' with 'is a' -> should find 116680003 | SNOMED Internal UK instance (Snowstorm)...")
    instance = GenericSnomedInstance("http://snowstorm-uk.misit-augsburg.de", branch="MAIN/2023-08-30", branch_encode=False)
    print(json.dumps(instance.search_term_by_browse_descriptions(term, limit=2, semanticTags=tag), indent=4))
    print()

    term="is a"
    tag = ["finding", "substance"]
    print("SemanticTag 'finding', 'substance' with 'is a' -> should not find 116680003 | SNOMED Internal UK instance (Snowstorm)...")
    instance = GenericSnomedInstance("http://snowstorm-uk.misit-augsburg.de", branch="MAIN/2023-08-30", branch_encode=False)
    print(json.dumps(instance.search_term_by_browse_descriptions(term, limit=2, semanticTags=tag), indent=4))
    print()

    term="is a"
    tag = ["finding", "attribute", "substance"]
    print("SemanticTag 'finding', 'attribute', 'substance' with 'is a' -> should find 116680003 | SNOMED Internal UK instance (Snowstorm)...")
    instance = GenericSnomedInstance("http://snowstorm-uk.misit-augsburg.de", branch="MAIN/2023-08-30", branch_encode=False)
    print(json.dumps(instance.search_term_by_browse_descriptions(term, limit=2, semanticTags=tag), indent=4))
    print()