import re, json, os
from functools import reduce
from textwrap import dedent, indent
from typing import Dict, Optional, List, Tuple

import outlines
from outlines import models
from transformers import AutoModelForCausalLM, AutoTokenizer

from infherno.tools.fhircodes.codings import listSupportedCodings


dpath = os.path.dirname(os.path.realpath(__file__))
repo_path = os.path.dirname(dpath)

MAX_COUNT_NOSEARCH = 10 # If <=10, just paste all results in the chat
MAX_SEARCH_RESULTS = 10 # If >10, only show 10 results (truncated)
MAX_SEARCH_QUERIES = 3  # Only perform 3 search attempts at max

def _make_system_prompt() -> str:
    system_prompt = dedent("""\
        You are a bot that tries to find the correct code and system for a given search term while taking the context of the term into account.
        You can re-phrase the search term {} times. In that case, rephrase the search term with the following line:
        [Code Search] Retry search for `<query_term>`

        If the corresponding code is found, the code is chosen with the following line:
        [Result] Select code: `<found_code>`
        If you cannot determine a matching code at all, the following line is used:
        [Result] No matching code found.

        Only decide to discard the found codes if really no entry matches at all.
        """
    ).format(
        MAX_SEARCH_QUERIES-1,
    ).strip()
    return system_prompt


FEW_SHOT_DESCRIPTORS = [{
    "system": _make_system_prompt(),
    "input_text": "Erwähnung von Magenbeschwerden. Etc...!",
    "quote": "Magenbeschwerden",
    "path": "Condition.code",
    "queries": [{
        "query": "Stomach ache",
        "results": [
            {
                'code': '271681002',
                'system': 'http://snomed.info/sct',
                'description': 'Stomach ache (finding)'
            }
        ],
        "truncated": False
    }],
    "result": {
        'code': '271681002',
        'system': 'http://snomed.info/sct',
        'description': 'Stomach ache (finding)'
    }
}]

VALID_STATES = [
    "SELECT_ACTION_RETRY_RETURN",
    "RETRY",
    "PICK",
    "DONE"
]

def descriptor2state(descriptor: Dict) -> str:
    if "system" not in descriptor:
        raise ValueError("Entry system not found")
    if "input_text" not in descriptor:
        raise ValueError("Entry input_text not found")
    if "quote" not in descriptor:
        raise ValueError("Entry quote not found")
    if "path" not in descriptor:
        raise ValueError("Entry path not found")
    if "queries" not in descriptor:
        raise ValueError("Entry queries not found")

    queries = descriptor["queries"]
    if not queries:
        raise ValueError("Entry queries is empty")

    if queries[0].get("query") is None:
        raise ValueError("First query entry not found")

    state = "SELECT_ACTION_RETRY_RETURN"
    for i, query in enumerate(queries):
        if "query" not in query:
            state = "RETRY"
        else:
            state = "SELECT_ACTION_RETRY_RETURN"

    if len(queries) >= MAX_SEARCH_QUERIES and "query" not in queries[-1]:
        state = "PICK"

    if "result" in descriptor:
        if descriptor.get("result") is None:
            state = "PICK"
        else:
            state = "DONE"

    return state

def descriptor2chat(descriptor: Dict) -> Dict:
    chat_entries = []

    # Add system prompt if given and non-blank
    if descriptor.get("system"):
        chat_entries.append(
            {"role": "system", "content": descriptor.get("system")}
        )

    input_msg = "The text is as follows:\n```\n{}\n```\n".format(descriptor.get("input_text"))
    input_msg += "The code search is for the phrase `{}` in the path `{}`.\n".format(descriptor.get("quote"), descriptor.get("path"))
    chat_entries.append(
        {"role": "user", "content": input_msg}
    )

    assistant_text = ""
    for i, queryItem in enumerate(descriptor.get("queries", [])):
        # Render search selection
        assistant_text += "[Code Search]"
        n_remaining = MAX_SEARCH_QUERIES - (i+1)

        if "query" in queryItem:
            # Render search prompt
            query = queryItem["query"]
            if i == 0:
                assistant_text += f" Search for `{query}` ({n_remaining} search attempts left):\n"
            elif i > 0 and n_remaining >= 0:
                assistant_text += f" Retry search for `{query}` ({n_remaining} search attempts left):\n"
            else:
                raise ValueError("Too many search attempts")

            # Render results
            if "results" in queryItem:
                assistant_text += "Results:\n"
                results = queryItem.get("results", [])
                if not results:
                    assistant_text += "No results found\n"
                else:
                    for resultItem in results:
                        assistant_text += f"  - Code '{resultItem['code']}' (System '{resultItem['system']}') [{resultItem['description']}]\n"

                if queryItem.get("truncated", False):
                    assistant_text += "(Further results were truncated)\n"

    if "result" in descriptor:
        # Render result
        assistant_text += "[Result]"
        result = descriptor.get("result", None)
        if result is None:
            # It is undecided whether a result is found or not
            pass
        elif not result:
            assistant_text += " No matching code found.\n[Done]\n"
        else:
            assistant_text += f" Select code: '{result['code']}' (System '{result['system']}')\n[Done]\n"

    chat_entries.append(
        {"role": "assistant", "content": assistant_text }
    )

    return chat_entries

def chat2tt(tokenizer: "AutoTokenizer", chat: Dict, examples: List[Dict] = None) -> Tuple[List[int], str]:
    global FEW_SHOT_DESCRIPTORS
    if examples is None:
        examples = FEW_SHOT_DESCRIPTORS

    example_tokens = reduce(lambda x,y: x+y,
        [ tokenizer.apply_chat_template(descriptor2chat(example), tokenize=True) for example in examples ]
    ) if examples else []

    # check if it ends with [Done]
    tokens_done = tokenizer.apply_chat_template([{"role": "assistant", "content": "\n[Done]\n"}], tokenize=True)
    tokens = example_tokens + tokenizer.apply_chat_template(chat, tokenize=True)

    if (tokens[-len(tokens_done):] == tokens_done):
        # We are done
        pass
    else:
        # Remove the last '<|eot_id|>' because we are not done yet
        tokens = tokens[:-1]

    text = tokenizer.decode(tokens)
    return tokens, text

def execute_actions(model: "AutoModelForCausalLM", tokenizer: "AutoTokenizer", descriptor: Dict) -> Dict:
    state = descriptor2state(descriptor)
    chat = descriptor2chat(descriptor)
    tokens, text = chat2tt(tokenizer, chat)

    ol_model = models.Transformers(model, tokenizer)

    updated_descriptor = descriptor.copy()
    if state == "SELECT_ACTION_RETRY_RETURN":
        print(f"We are in state: SELECT_ACTION_RETRY_RETURN")

        # We can select from 'Code Search' or 'Result' (if we don't exceed the max search queries)
        options_left = MAX_SEARCH_QUERIES - len(updated_descriptor["queries"])
        if options_left > 0:
            action_generator = outlines.generate.choice(ol_model, ["[Code Search]", "[Result]"])
            selected_action = action_generator(text)
        else:
            selected_action = "[Result]"

        if selected_action == "[Code Search]":
            # We re-try with a new search term search...
            updated_descriptor["queries"].append({})

        if selected_action == "[Result]":
            updated_descriptor["result"] = None

    if state == "RETRY":
        print(f"We are in state: RETRY")
        pattern = r" Retry search for `([^\n`]+)`"
        generator = outlines.generate.regex(ol_model, pattern)
        retry_text = generator(text)
        retry_match = re.match(pattern, retry_text)
        if not retry_match: raise ValueError(f"Unable to match text: {repr(retry_text)}")

        # Extract term
        query_term = retry_match.group(1)

        queries = updated_descriptor["queries"].copy()
        recent_query = queries[-1].copy()

        from infherno.tools.fhircodes.instance import GenericSnomedInstance
        from infherno.tools.fhircodes.codings import listSupportedCodings, getValueSet, ValueSetLoader

        path = descriptor.get("path")
        assert path in listSupportedCodings(), f"Path '{path}' is not supported"
        vs_info = getValueSet(path)

        instance = GenericSnomedInstance("http://snowstorm-uk.misit-augsburg.de", branch="MAIN/2023-08-30", branch_encode=False)
        vsl = ValueSetLoader.from_url(vs_info["vs"], store_threshold=20, snomed_instance=instance)

        # Search for term....
        if vsl.count() < MAX_COUNT_NOSEARCH:
            results = vsl.search("")
        else:
            results = vsl.search(query_term, limit=MAX_SEARCH_RESULTS)
            if len(results) == MAX_SEARCH_RESULTS:
                recent_query["truncated"] = True
            else:
                recent_query["truncated"] = False

        # Write results
        recent_query["query"] = query_term
        recent_query["results"] = results
        queries[-1] = recent_query
        updated_descriptor["queries"] = queries

    if state == "PICK":
        print(f"We are in state: PICK")

        # Collect all possible results
        all_candidates = reduce(lambda x,y: x+y, [
            query.get("results", []) for query in updated_descriptor["queries"]
        ])

        # Pick none if no candidates were found
        if not all_candidates:
            picked_result = {}
        else:
            # Decide on whether to pick a code or not
            choices = [
                "No matching code found.",
                "Select code:"
            ]
            choices_generator = outlines.generate.choice(ol_model, choices)
            choice = choices_generator(text + " ")
            if choice == "No matching code found.":
                picked_result = {}
            else:
                # Query a code
                all_candidate_codes = [ c["code"] for c in all_candidates ]
                unique_code_items = list(set(all_candidate_codes))

                # sample a result
                code_generator = outlines.generate.choice(ol_model, unique_code_items)
                code = code_generator(text + " Select code: '")

                picked_result = code

                # find the corresponding code item
                for candidate in all_candidates:
                    if candidate["code"] == code:
                        picked_result = candidate

        updated_descriptor["result"] = picked_result

    if state == "DONE":
        print(f"We are in state: DONE")
        # Don't do anything...
        pass

    return updated_descriptor

def code_search(
        input_text: str,
        path: str,
        quote: str,
        query: str,
        trf_tokenizer: "AutoTokenizer",
        trf_model: "AutoModelForCausalLM"
    ) -> Optional[Dict]:

    # Initial search
    from infherno.tools.fhircodes.instance import GenericSnomedInstance
    from infherno.tools.fhircodes.codings import listSupportedCodings, getValueSet, ValueSetLoader

    assert path in listSupportedCodings(), f"Path '{path}' is not supported"
    vs_info = getValueSet(path)

    instance = GenericSnomedInstance("http://snowstorm-uk.misit-augsburg.de", branch="MAIN/2023-08-30", branch_encode=False)
    vsl = ValueSetLoader.from_url(vs_info["vs"], store_threshold=20, snomed_instance=instance)

    # Search for term....
    if vsl.count() < MAX_COUNT_NOSEARCH:
        initial_results = vsl.search("")
    else:
        initial_results = vsl.search(query, limit=MAX_SEARCH_RESULTS)

    initial_descriptor = {
        "system": _make_system_prompt(),
        "input_text": input_text,
        "quote": quote,
        "path": path,
        "queries": [{
            "query": query,
            "results": initial_results,
            "truncated": len(initial_results) == MAX_SEARCH_RESULTS
        }]
    }

    current_descriptor = initial_descriptor
    while True:
        current_descriptor = execute_actions(trf_model, trf_tokenizer, current_descriptor)
        # Check if the agent has terminated
        if current_descriptor.get("result", None) is not None:
            break

    return current_descriptor["result"]

def runDemo(input_text, path, quote, query, model_path):
    trf_tokenizer = AutoTokenizer.from_pretrained(model_path)
    trf_model = AutoModelForCausalLM.from_pretrained(model_path).to("cuda")
    #ol_model = models.Transformers(trf_model, trf_tokenizer)

    # Initial search
    from infherno.tools.fhircodes.instance import GenericSnomedInstance
    from infherno.tools.fhircodes.codings import listSupportedCodings, getValueSet, ValueSetLoader

    assert path in listSupportedCodings(), f"Path '{path}' is not supported"
    vs_info = getValueSet(path)

    instance = GenericSnomedInstance("http://snowstorm-uk.misit-augsburg.de", branch="MAIN/2023-08-30", branch_encode=False)
    vsl = ValueSetLoader.from_url(vs_info["vs"], store_threshold=20, snomed_instance=instance)

    # Search for term....
    if vsl.count() < MAX_COUNT_NOSEARCH:
        initial_results = vsl.search("")
    else:
        initial_results = vsl.search(query, limit=MAX_SEARCH_RESULTS)


    initial_descriptor = {
        "system": _make_system_prompt(),
        "input_text": input_text,
        "quote": quote,
        "path": path,
        "queries": [{
            "query": query,
            "results": initial_results,
            "truncated": len(initial_results) == MAX_SEARCH_RESULTS
        }]
    }

    current_descriptor = initial_descriptor
    print("Initial Descriptor:")
    print(json.dumps(current_descriptor, indent=2))
    print("---"*4)
    while True:
        current_descriptor = execute_actions(trf_model, trf_tokenizer, current_descriptor)
        print("Prompt text:")
        print(chat2tt(trf_tokenizer, descriptor2chat(current_descriptor), examples=[])[1])
        print("---"*4)
        print("Current Descriptor:")
        print(json.dumps(current_descriptor, indent=2))
        print("---"*4)
        #if input("Continue? (Y/n)").strip() == "n":
        if current_descriptor.get("result", None) is not None:
            break

    return current_descriptor

if __name__ == "__main__":
    # runDemo(
    #     "Einnahme von starkem Morphin (2x am Tag, 150mg)",
    #     "MedicationStatement.medication",
    #     "Morphin",
    #     "Morphine",
    #     "meta-llama/Llama-3.1-8B-Instruct"
    # )
    # runDemo(
    #     "Sehr geehrte Damen und Herren, ....... ein Ekzem im Gesicht....",
    #     "Condition.code",
    #     "Ekzem",
    #     "eczema",
    #     "meta-llama/Llama-3.1-8B-Instruct"
    # )
    runDemo(
        "Sehr geehrte Damen und Herren, ....... ein Ekzem im Gesicht....",
        "Condition.bodySite",
        "Ekzem im Gesicht",
        "face",
        "meta-llama/Llama-3.1-8B-Instruct"
    )