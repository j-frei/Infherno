from datasets import Dataset, load_dataset


def load_cardiode(data_path: str = "../CARDIODE400_main@deanonymized_slim.jsonl") -> Dataset:
    raw_dataset = load_dataset("json", data_files=data_path)["train"]
    return raw_dataset


def load_n2c2(data_path: str = "../n2c2_gold@deanonymized_slim.jsonl") -> Dataset:
    raw_dataset = load_dataset("json", data_files=data_path)["train"]
    return raw_dataset
