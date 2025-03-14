import re, random, json, os
import outlines
from outlines import models
from transformers import AutoModelForCausalLM, AutoTokenizer
from textwrap import dedent, indent
from functools import reduce

from infherno.samples.text2fhir import getSamples
from infherno.tools.fhircodes.codings import listSupportedCodings
from infherno.codesearch import code_search
from infherno.utils import determine_device

dpath = os.path.dirname(os.path.realpath(__file__))
repo_path = os.path.dirname(dpath)
grammar_path = os.path.join(repo_path, "grammar", "fhir_grammar.ebnf")

SUPPORTED_FHIR_RESOURCES = [
    "Patient",
    #"Organization",
    #"Practitioner",
    #"Encounter",
    "Procedure",
    #"Observation",
    "Condition",
    "MedicationStatement",
]

def _make_system_prompt():
    supported_fhir_codings = [ c for c in listSupportedCodings() if any([c.startswith(r + ".") for r in SUPPORTED_FHIR_RESOURCES]) ]
    system_prompt = dedent("""\
        You are a bot that
        - reads an input text from the user,
        - selects from the following actions with the following patterns:
          - FHIR code search to retrieve the codes and system for a given search term.
            The pattern looks as follows: [Code Search] For phrase `context_quote` search for `query_term` in `fhir_coding`: `found_code` @ system 'code_system'"
            If the code is not a CodableConcept but can be used directly, only the `found_code` is provided without the suffix: @ system `code_system`.
            Query all required FHIR codings that are needed to generate the FHIR resources, before you even generate the actual FHIR resources, except for the Units of Measure code system!
            The supported FHIR codings are:
        {}
          - FHIR output to generate the FHIR resources.
            The pattern looks as follows: [FHIR Output]\\n```\\nfhir resource\\n```'"
            Prefer CodeableConcepts whenever possible over CodableReference.
            The supported FHIR resources are:
        {}
          - Done to signal the stop of the agent loop.
            Only exit the agent loop without FHIR outputs, if the input text does not contain any information which could be translated into a reasonable FHIR resource!
            The pattern looks as follows: [Done]
        """
    ).format(
        indent('\n'.join(supported_fhir_codings), '    - '),
        indent('\n'.join(SUPPORTED_FHIR_RESOURCES), '    - ')
    ).strip()
    return system_prompt

FEW_SHOT_DESCRIPTORS = list(getSamples(_make_system_prompt()))

VALID_STATES = [
    "SELECT_ACTION_CODESEARCH_FHIROUTPUT_DONE_CODESEARCH_FHIROUTPUT_DONE",
    "PREDICT_PATH_QUOTE_QUERY",
    "CODE_SEARCH",
    "SELECT_ACTION_FHIROUTPUT_DONE"
    "FHIR_OUTPUT",
    "DONE"
]

def descriptor2state(descriptor):
    if "system" not in descriptor:
        raise ValueError("Entry system not found")
    if "input_text" not in descriptor:
        raise ValueError("Entry input_text not found")

    state = "SELECT_ACTION_CODESEARCH_FHIROUTPUT_DONE"
    if descriptor.get("codes"):
        for codeitem in descriptor.get("codes", []):
            if not codeitem:
                # Only action is selected
                state = "PREDICT_PATH_QUOTE_QUERY"
            else:
                if "quote" not in codeitem or \
                    "path" not in codeitem or \
                    "query" not in codeitem:
                    raise ValueError("Code item misses quote, path or query.")
                state = "CODE_SEARCH"

                if "code" in codeitem:
                    state = "SELECT_ACTION_CODESEARCH_FHIROUTPUT_DONE"

    if "fhir" in descriptor:
        state = "SELECT_ACTION_FHIROUTPUT_DONE"
        for fhirItem in descriptor.get("fhir", []):
            if not fhirItem:
                state = "FHIR_OUTPUT"

    if descriptor.get("finished", False):
        state = "DONE"

    return state

def descriptor2chat(descriptor: dict) -> dict:
    chat_entries = []

    # Add system prompt if given and non-blank
    if descriptor.get("system"):
        chat_entries.append(
            {"role": "system", "content": descriptor.get("system")}
        )
    if descriptor.get("input_text"):
        input_msg = "The text is as follows:\n```\n{}\n```\n".format(descriptor.get("input_text"))
        chat_entries.append(
            {"role": "user", "content": input_msg}
        )

    assistant_text = ""
    if descriptor.get("codes") is not None:
        for codeItem in descriptor.get("codes", []):
            assistant_text += "[Code Search]"
            if codeItem:
                quote = codeItem["quote"]
                query = codeItem["query"]
                path = codeItem["path"]

                assistant_text += f" For phrase `{quote}` search for `{query}` in `{path}`:"
                if "code" in codeItem:
                    code = codeItem["code"]
                    if code:
                        assistant_text += f" `{code}`"
                        if "system" in codeItem:
                            system = codeItem["system"]
                            if system:
                                assistant_text += f" @ system '{system}'"
                        assistant_text += "\n"
                    else:
                        assistant_text += " unknown\n"

    if "fhir" in descriptor:
        for fhirItem in descriptor.get("fhir", []):
            assistant_text += "[FHIR Output]\n```\n"
            if fhirItem:
                assistant_text += fhirItem.strip()
                assistant_text += "\n```\n"

    if descriptor.get("finished", False):
        assistant_text += "[Done]\n"
    # else:
    #     # The FHIR output is not done -> add initial FHIR_OUTPUT to prompt
    #     assistant_text += "[FHIR Output]\n```\n"

    chat_entries.append(
        {"role": "assistant", "content": assistant_text }
    )

    return chat_entries

def chat2tt(tokenizer, chat, examples=None):
    global FEW_SHOT_DESCRIPTORS
    if examples is None:
        examples = FEW_SHOT_DESCRIPTORS

    example_tokens = reduce(lambda x,y: x+y,
        [ tokenizer.apply_chat_template(descriptor2chat(example), tokenize=True) for example in examples ]
    , []) if examples else []

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

FHIR_CFG_GENERATOR = None
def execute_actions(model, tokenizer, descriptor):
    global FHIR_CFG_GENERATOR
    if FHIR_CFG_GENERATOR is None:
        FHIR_CFG_GENERATOR = {}

    state = descriptor2state(descriptor)
    chat = descriptor2chat(descriptor)
    tokens, text = chat2tt(tokenizer, chat)

    ol_model = models.Transformers(model, tokenizer)
    if tokenizer.name_or_path not in FHIR_CFG_GENERATOR:
        with open(grammar_path, "r") as f:
            grammar = f.read()
        FHIR_CFG_GENERATOR[tokenizer.name_or_path] = outlines.generate.cfg(ol_model, grammar)

    updated_descriptor = descriptor.copy()
    if state == "SELECT_ACTION_CODESEARCH_FHIROUTPUT_DONE":
        print(f"We are in state: SELECT_ACTION_CODESEARCH_FHIROUTPUT_DONE")
        # We can select from 'Code Search', 'FHIR Output' and 'Done'
        action_generator = outlines.generate.choice(ol_model, ["[Code Search]", "[FHIR Output]", "[Done]"])
        selected_action = action_generator(text)

        # Make sure that codes exists
        if "codes" not in updated_descriptor:
            updated_descriptor["codes"] = []

        if selected_action == "[Code Search]":
            updated_descriptor["codes"].append({})

        if selected_action == "[FHIR Output]":
            # Make sure that fhir exists
            if "fhir" in updated_descriptor:
                raise ValueError("The fhir property is already set.")

            updated_descriptor["fhir"] = []

        if selected_action == "[Done]":
            updated_descriptor["finished"] = True
    if state == "PREDICT_PATH_QUOTE_QUERY":
        print(f"We are in state: PREDICT_PATH_QUOTE_QUERY")
        supported_fhir_paths = r'|'.join([ re.escape(r) for r in listSupportedCodings() ])
        pattern = r" For phrase `([^\n`]+)` search for `([^\n`]+)` in `({})`:".format(supported_fhir_paths)
        generator = outlines.generate.regex(ol_model, pattern)
        pqq_text = generator(text)
        match = re.match(pattern, pqq_text)
        if not match: raise ValueError(f"Unable to match text: {repr(pqq_text)}")

        quote = match.group(1)
        query = match.group(2)
        path = match.group(3)
        codes = updated_descriptor["codes"].copy()
        recent_code = codes[-1].copy()
        recent_code = {
            **recent_code,
            "quote": quote,
            "query": query,
            "path": path
        }
        codes[-1] = recent_code
        updated_descriptor["codes"] = codes

    if state == "CODE_SEARCH":
        print(f"We are in state: CODE_SEARCH")
        # TODO: Generate Code Search
        codes = updated_descriptor["codes"].copy()
        recent_code = codes[-1].copy()

        query = recent_code["query"]
        quote = recent_code["quote"]
        path = recent_code["path"]

        # Trigger CodeSearch
        code_result = code_search(descriptor["input_text"], path, quote, query, tokenizer, model)

        if "code" in code_result:
            recent_code["code"] = code_result["code"]

            if "system" in code_result:
                system = code_result["system"]
                if not system.startswith("http://hl7.com"):
                    recent_code["system"] = system
        else:
            recent_code["code"] = None

        codes[-1] = recent_code
        updated_descriptor["codes"] = codes
    if state == "SELECT_ACTION_FHIROUTPUT_DONE":
        print(f"We are in state: SELECT_ACTION_FHIROUTPUT_DONE")
        # We can select from 'FHIR Output' and 'Done'
        action_generator = outlines.generate.choice(ol_model, ["[FHIR Output]", "[Done]"])
        selected_action = action_generator(text)

        # Make sure that codes exists
        if "fhir" not in updated_descriptor:
            updated_descriptor["fhir"] = []

        if selected_action == "[FHIR Output]":
            # Add empty FHIR output
            updated_descriptor["fhir"].append(None)

        if selected_action == "[Done]":
            updated_descriptor["finished"] = True

    if state == "FHIR_OUTPUT":
        print(f"We are in state: FHIR_OUTPUT")
        if len(updated_descriptor["fhir"]) > 0 and updated_descriptor["fhir"][-1] is not None:
            raise ValueError("The last FHIR output is not None.")

        generator = FHIR_CFG_GENERATOR[tokenizer.name_or_path]
        fhir_text = generator(text+'\n', max_tokens=4096)
        updated_descriptor["fhir"][-1] = fhir_text

    if state == "DONE":
        print(f"We are in state: DONE")
        # Don't do anything...
        pass

    return updated_descriptor

def run(input_text, model_path):
    trf_tokenizer = AutoTokenizer.from_pretrained(model_path)
    trf_model = AutoModelForCausalLM.from_pretrained(model_path).to(determine_device())

    descriptor = {
        "system": _make_system_prompt(),
        "input_text": input_text,
    }

    current_descriptor = descriptor
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
        if current_descriptor.get("finished", False):
            break

    with open("out.json", "w") as f:
        json.dump(current_descriptor, f, indent=2)
    return current_descriptor

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the text2fhir model.")
    parser.add_argument("input_text", type=str, help="The input text to process.")
    parser.add_argument("model_path", type=str, help="The model path to use.")
    parser.add_argument("--action", type=str, default="text2fhir", choices=["text2fhir", "yield_prompt"], help="The action to perform.")
    args = parser.parse_args()

    if args.action == "text2fhir":
        result = run(args.input_text, args.model_path)
        print("Found FHIR Resources:")
        for fhirItem in result.get("fhir", []):
            print(fhirItem)
        if not result.get("fhir", []):
            print("No FHIR resources found.")
    elif args.action == "yield_prompt":
        # We just need any reasonable tokenizer
        tokenizer = AutoTokenizer.from_pretrained(args.model_path if args.model_path else "meta-llama/Llama-3.1-8B-Instruct")
        descriptor = {
            "system": _make_system_prompt(),
            "input_text": args.input_text,
        }
        text = chat2tt(tokenizer, descriptor2chat(descriptor))[1]
        print(text)