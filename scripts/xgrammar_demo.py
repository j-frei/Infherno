import os, time
import xgrammar as xgr
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

from utils import determine_device


dpath = os.path.dirname(os.path.realpath(__file__))
repo_path = os.path.dirname(dpath)

device = determine_device()

# Loading the model
print("Loading model...")
model_id = "meta-llama/Llama-3.1-8B-Instruct"
trf_tokenizer = AutoTokenizer.from_pretrained(model_id)
trf_model = AutoModelForCausalLM.from_pretrained(model_id)
trf_model.to(device)
trf_config = AutoConfig.from_pretrained(model_id)

# Loading the grammar
print("Loading grammar...")
grammar_path = os.path.join(repo_path, "grammar", "fhir_grammar_xgrammar.gbnf")
with open(grammar_path, "r") as f:
    grammar = f.read().strip()

# Preparing the input text
prompt = """
The medication is about Advil which has the code M01AE01 according to the ATC classification.
The medication is taken orally and the dose is 200mg.
The statement is to take the medication once daily.

A FHIR resource should look as follows, when only the stated information are considered:
""".strip() + "\n"

model_inputs = trf_tokenizer(prompt, return_tensors="pt").to(trf_model.device)

print("Building CFG generator...")
print("Starting at: ", time.ctime())
tokenizer_info = xgr.TokenizerInfo.from_huggingface(trf_tokenizer, vocab_size=trf_config.vocab_size)
grammar_compiler = xgr.GrammarCompiler(tokenizer_info, max_threads=1)

compiled_grammar = grammar_compiler.compile_grammar(grammar)
#with open(os.path.join(dpath, "fhir_schema.json"), "r") as f:
#    schema = f.read().strip()

#compiled_grammar = xgr.Grammar.from_json_schema(schema)
print("Done at: ", time.ctime())

xgr_logits_processor = xgr.contrib.hf.LogitsProcessor(compiled_grammar)

print("Generating text...")
generated_ids = trf_model.generate(
    **model_inputs, max_new_tokens=1024, logits_processor=[xgr_logits_processor]
)

generated_text = trf_tokenizer.decode(generated_ids[0], skip_special_tokens=True)
print("Final output:")
print(generated_text)
