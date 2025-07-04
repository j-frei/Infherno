from typing import List, Dict
import os
import re
from glob import glob
from functools import reduce

import pandas as pd

anno_dir = "../data/synthetic_gt"
markdown_files = list(sorted(
    [ f for f in glob(os.path.join(anno_dir, "*.md")) if os.path.isfile(f) and not f.endswith("README.md") ],
   key=lambda x: int(os.path.splitext(os.path.basename(x))[0])
))

#sign_categories = ["=", "==", "+", "-", "+-", "X", "\\", "/"]
#quality_map = {"=": "Neutral", "==": "Neutral", "+": "Neutral", "-": "Neutral", "+-": "Neutral", "X": "Worse", "\\": "Worse", "/": "Better"}

def parse_file(file_path: str) -> List[dict]:
    with open(file_path, "r") as f:
        text = f.read()

    item_stats = []
    ptn_resource = re.compile(r"\* \[(?P<resource_flag>[^\]]+)\] (?P<resource_info>.*):")
    ptn_elements = re.compile(r"    \[(?P<element_flag>[^\]]+)\] (?P<comment>.+)")
    resources = [ m for m in ptn_resource.finditer(text) ]

    for i, m in enumerate(resources):
        outer_cruciality = "!" in m.group("resource_flag")
        if outer_cruciality: assert "?" not in m.group("resource_flag")
        if not outer_cruciality: assert "!" not in m.group("resource_flag")

        content_slice = slice(m.end(), (resources[i+1].start() if i + 1 < len(resources) else None))
        content = text[content_slice]

        elements = [ em for em in ptn_elements.finditer(content) ]

        for em in elements:
            element_flag = em.group("element_flag")

            # print("Processing resource:", m.group("resource_info") + " with element:", em.group("comment"), "and flag:", element_flag)

            element_cruciality = outer_cruciality
            if "?" in element_flag:
                element_cruciality = False
            if "!" in element_flag:
                element_cruciality = True

            element_negative = "\\" in element_flag
            element_positive = "/" in element_flag
            element_hallucination = "X" in element_flag

            if element_hallucination:
                element_negative = True

            element_total_equivalence = "==" in element_flag
            element_partial_equivalence = "==" not in element_flag and "=" in element_flag

            element_difference = "+-" in element_flag or "-+" in element_flag
            element_addition = "+" in element_flag and not element_difference
            element_lack = "-" in element_flag and not element_difference


            item_stats.append({
                "crucial": element_cruciality,
                "negative": element_negative,
                "positive": element_positive,
                "partial_equal": element_partial_equivalence,
                "total_equal": element_total_equivalence,
                "addition": element_addition,
                "lacking": element_lack,
                "difference": element_difference,
                "hallucinate": element_hallucination,
            })

    return item_stats


def stats_df():
    stats_stacked = reduce(lambda x,y: x+y, [ parse_file(file) for file in markdown_files ], [])
    return pd.DataFrame.from_records(stats_stacked)

df = stats_df()

# Crucial and Worse than GT
print("Crucial and Worse than GT:")
print(df[(df["crucial"]) & (df["negative"])].sum(numeric_only=True))
print()

print("Crucial and Neutral:")
print(df[(df["crucial"]) & (~df["positive"]) & (~df["negative"])].sum(numeric_only=True))
print()

print("Crucial and Better than GT:")
print(df[(df["crucial"]) & (df["positive"])].sum(numeric_only=True))
print()

print("-"*40)

# Non-Crucial and Worse than GT
print("Non-Crucial and Worse than GT:")
print(df[(~df["crucial"]) & (df["negative"])].sum(numeric_only=True))
print()

print("Non-Crucial and Neutral:")
print(df[(~df["crucial"]) & (~df["positive"]) & (~df["negative"])].sum(numeric_only=True))
print()

print("Non-Crucial and Better than GT:")
print(df[(~df["crucial"]) & (df["positive"])].sum(numeric_only=True))
print()

# Total better than GT, worse than GT, neutral
print("Total better than GT:")
print(len(df[df["positive"]]))
print()
print("Total worse than GT:")
print(len(df[df["negative"]]))
print()
print("Total neutral:")
print(len(df[~df["positive"] & ~df["negative"]]))
print()