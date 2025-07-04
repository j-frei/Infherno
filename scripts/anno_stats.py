import os
import re
from collections import defaultdict

anno_dir = "../data/synthetic_gt"
markdown_files = [f for f in os.listdir(anno_dir) if f.endswith(".md")]

sign_categories = ["=", "==", "+", "-", "+-", "X", "\\", "/"]
quality_map = {"=": "Neutral", "==": "Neutral", "+": "Better", "-": "Worse", "+-": "Neutral", "X": "Worse", "\\": "Worse", "/": "Better"}


def parse_annotations(file_path):
    counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    inherited = []

    with open(file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        indent = len(line) - len(line.lstrip())
        match = re.search(r'\[([^\]]+)\]', line)
        if match:
            signs = re.findall(r'(==|\+-|-\+|=|[!?+\-/\\X])', match.group(1))
            cruciality = '!' if '!' in signs else '?' if '?' in signs else inherited[-1][1] if inherited else '?'

            while inherited and inherited[-1][0] >= indent:
                inherited.pop()

            inherited.append((indent, cruciality))

            combined_signs = set(signs)
            combined_signs = {"+-" if s in {"+-", "-+"} else s for s in combined_signs}

            for sign in combined_signs:
                if sign in sign_categories:
                    quality = quality_map[sign]
                    counts[cruciality][sign][quality] += 1

    return counts


# Aggregate
agg_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

for md_file in markdown_files:
    file_counts = parse_annotations(os.path.join(anno_dir, md_file))
    for cruciality in file_counts:
        for sign in file_counts[cruciality]:
            for quality in file_counts[cruciality][sign]:
                agg_counts[cruciality][sign][quality] += file_counts[cruciality][sign][quality]


# Generate LaTeX Table
print(r"""\begin{tabular}{cl|>{\columncolor{lightred}}r>{\columncolor{lightyellow}}r>{\columncolor{lightgreen}}r}
\textbf{Sign} & \textbf{Description} & \textbf{Worse than GT} & \textbf{Neutral} & \textbf{Better than GT} \\
\toprule
""")

for cruciality in ['!', '?']:
    label = "crucial items" if cruciality == '!' else "non-crucial items"
    print(f"& & \multicolumn{{3}}{{c}}{{\texttt{{{cruciality}}} ({label})}} \\")
    print(r"\hdashline")

    for sign in ["=", "==", "+", "-", "+-", "X"]:
        worse = agg_counts[cruciality][sign]['Worse'] + agg_counts[cruciality]["\\"]['Worse']
        neutral = agg_counts[cruciality][sign]['Neutral']
        better = agg_counts[cruciality][sign]['Better'] + agg_counts[cruciality]["/"]['Better']

        descriptions = {
            "=": "(semantically related)",
            "==": "(completely identical)",
            "+": "(lacking in GT)",
            "-": "(lacking in PD)",
            "+-": "(value difference)",
            "X": "(hallucinated or invalid)",
        }

        description = descriptions[sign]
        print(f"\\texttt{{{sign}}} & {description} & {worse} & {neutral} & {better} \\\\")

    if cruciality == '!':
        print(r"\midrule")

print(r"\bottomrule")
print(r"\end{tabular}")
