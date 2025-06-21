from datasets import Dataset, load_dataset
from itertools import chain


def load_cardiode(data_path: str = "../CARDIODE400_main@deanonymized_slim.jsonl") -> Dataset:
    raw_dataset = load_dataset("json", data_files=data_path)["train"]
    return raw_dataset


def load_n2c2(data_path: str = "../n2c2_gold@deanonymized_slim.jsonl") -> Dataset:
    raw_dataset = load_dataset("json", data_files=data_path)["train"]
    new_dataset = raw_dataset.map(
        lambda ex: {"paragraphs": [p.strip() for p in ex["text"].split("\n\n") if p.strip()]},
        batched=False,
    )
    # 1) Pull out all your paragraph lists
    all_paragraphs = list(chain.from_iterable(new_dataset["paragraphs"]))
    # 2) Drop any empty / whitespace-only strings
    all_paragraphs = [p.strip() for p in all_paragraphs if p.strip()]
    # 3) Build a brand-new Dataset
    new_dataset = Dataset.from_list([{"text": p} for p in all_paragraphs])
    return new_dataset
