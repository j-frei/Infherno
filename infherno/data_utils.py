import re
from datasets import Dataset, load_dataset


N2C2_HEADER_RE = re.compile(r"^[A-Z][A-Z0-9 /]+:\s*$")


def apply_partitioning(raw_dataset):
    def merge_by_headers(paragraphs):
        groups, current = [], []
        for p in paragraphs:
            if N2C2_HEADER_RE.match(p):
                if current:
                    groups.append("\n\n".join(current))
                current = [p]
            else:
                current.append(p)
        if current:
            groups.append("\n\n".join(current))
        return groups

    def merge_by_length(paragraphs, min_chars=200):
        merged = []
        buffer = ""

        for p in paragraphs:
            if len(buffer) < min_chars:
                buffer = (buffer + "\n\n" + p).strip()
            else:
                merged.append(buffer)
                buffer = p
        if buffer:
            merged.append(buffer)

        return [{"text": m} for m in merged]

    split_ds = raw_dataset.map(
        lambda ex: {"paragraphs": [p.strip() for p in ex["text"].split("\n\n") if p.strip()]},
        batched=False,
    )
    # 2. manually walk through and apply both merges
    records = []
    for ex in split_ds:
        # carry over all original fields except the big text blob
        meta = {k: ex[k] for k in ex if k not in ("text", "paragraphs")}
        # 2a) header‐based grouping
        for section in merge_by_headers(ex["paragraphs"]):
            paras = section.split("\n\n")
            # 2b) length‐based sub‐splitting
            for chunk in merge_by_length(paras, min_chars=300):
                records.append({**meta, "text": chunk})

    # 3. rebuild your Dataset
    new_ds = Dataset.from_list(records)
    new_ds = new_ds.map(
        lambda ex: {"text": ex["text"]["text"]},
        batched=False,
        remove_columns=["text", "label", "i2o"]
    )
    return new_ds


def load_dummy() -> Dataset:
    dummy_str = ("Magenbeschwerden seit 2 Tagen, Übelkeit, Erbrechen, kein Durchfall.\n"
                 "Patient hat eine Allergie gegen Penicillin, keine weiteren Allergien bekannt.\n"
                 "Verschrieben wurde deshalb Pantoprazol 20mg 1-0-1.")
    dataset = Dataset.from_dict({"text": [dummy_str]})
    return dataset


def load_cardiode(data_path: str = f"./") -> Dataset:
    raw_dataset = load_dataset("json", data_files=data_path + "CARDIODE400_main@deanonymized_slim.jsonl")["train"]
    return raw_dataset


def load_n2c2(data_path: str = f"./") -> Dataset:
    raw_dataset = load_dataset("json", data_files=data_path + "n2c2_gold@deanonymized_slim.jsonl")["train"]
    # Add unique IDs (int)
    raw_dataset = raw_dataset.map(
        lambda example, idx: {"id": idx},
        with_indices=True,  # pass the example’s integer index into your fn
        batched=False
    )
    return raw_dataset


def load_synthetic(data_path: str = f"./") -> Dataset:
    raw_dataset = load_dataset(
        "text",
        data_files={"train": data_path + 'data/synthetic/*.txt'},
        sample_by="document",
    )["train"]
    return raw_dataset
