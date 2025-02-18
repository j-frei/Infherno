import os
import outlines
import time
from outlines import models
from transformers import AutoModelForCausalLM, AutoTokenizer

from scripts.utils import *


dpath = os.path.dirname(os.path.realpath(__file__))

device = determine_device()

# Loading the model
print("Loading model...")
model_id = "meta-llama/Llama-3.1-8B-Instruct"
trf_tokenizer = AutoTokenizer.from_pretrained(model_id)
trf_model = AutoModelForCausalLM.from_pretrained(model_id)
trf_model.to(device)

ol_model = models.Transformers(trf_model, trf_tokenizer)

# Loading the grammar
print("Loading grammar...")
grammar_path = os.path.join(dpath, "fhir_grammar.ebnf")
with open(grammar_path, "r") as f:
    grammar = f.read()

print("Building CFG generator...")
print("Starting at: ", time.ctime())
generator = outlines.generate.cfg(ol_model, grammar)
print("Done at: ", time.ctime())

print("Generating text...")
prompt = """
The medication is about Advil which has the code M01AE01 according to the ATC classification.
The medication is taken orally and the dose is 200mg.
The statement is to take the medication once daily.

A FHIR resource should look as follows, when only the stated information are considered:
""".strip() + "\n"

print(prompt, end="")
# Outlines also supports streaming output
stream = generator.stream(prompt, max_tokens=1024)
while True:
    try:
        token = next(stream)
        print(token, end="", flush=True)

    except StopIteration:
        break
    except Exception as e: # noqa
        print("\nError:", e)
        break

generated_text = generator(prompt)

print("Final output:")
print(prompt + generated_text)
