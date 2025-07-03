import os
import re
from collections import defaultdict

anno_dir = "../data/synthetic_gt"
markdown_files = [f for f in os.listdir(anno_dir) if f.endswith(".md")]

taxonomy_signs = ["?", "!", "+", "-", "/", "\\", "X", "=", "=="]


def parse_markdown_annotations(file_path):
    counts = defaultdict(int)
    total_annotations = 0
    inherited = []

    with open(file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        indent_level = len(line) - len(line.lstrip())
        match = re.search(r'\[([^\]]+)\]', line)
        if match:
            total_annotations += 1  # Every line with annotation counts as one
            signs = match.group(1)
            signs_split = re.findall(r'(==|=|[!?+\-/\\X])', signs)

            # Update inheritance stack
            while inherited and inherited[-1][0] >= indent_level:
                inherited.pop()

            current_signs = set(signs_split)

            # Inherit from parents if not overridden
            for lvl, parent_signs in inherited:
                current_signs.update(parent_signs)

            for sign in current_signs:
                counts[sign] += 1

            inherited.append((indent_level, current_signs))

    return counts, total_annotations


# Aggregating across files
agg_counts = defaultdict(int)
agg_total_annotations = 0

for md_file in markdown_files:
    file_path = os.path.join(anno_dir, md_file)
    counts, total_annotations = parse_markdown_annotations(file_path)
    agg_total_annotations += total_annotations
    for sign, count in counts.items():
        agg_counts[sign] += count

# Generate LaTeX table
print(r"\begin{tabular}{lcc}")
print(r"\textbf{Sign} & \textbf{Count} & \textbf{Ratio}\\")
print(r"\hline")

sign_descriptions = {
    "?": "optional, not pressing",
    "!": "crucial, important",
    "+": "Present in PD (Lacks in GT)",
    "-": "Lacking in PD (Present in GT)",
    "/": "Better than GT",
    "\\": "Worse than GT",
    "X": "Hallucination or Invalid",
    "=": "Semantically identical",
    "==": "(nearly) completely identical"
}

for sign in taxonomy_signs:
    count = agg_counts.get(sign, 0)
    ratio = f"{count}/{agg_total_annotations}" if agg_total_annotations else "-"
    description = sign_descriptions[sign]
    print(f"{sign} ({description}) & {count} & {ratio} \\\\")

print(r"\end{tabular}")

