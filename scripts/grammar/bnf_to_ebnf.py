from bnf_rule_tokenizer import tokenize_rule, RuleToken, RuleTokenType

def rule_gbnf_to_ebnf(rule_line: str) -> str:
    tokens = list(tokenize_rule(rule_line))
    rule_str = ""
    skip = False
    for i, t in enumerate(tokens):
        if skip:
            skip = False
            continue

        if t.ttype == RuleTokenType.RULE:
            rule_name = t.val
            if rule_name == "root":
                rule_name = "start"

            ebnf_rule = rule_name.replace("-", "_").lower()
            if i == 0:
                rule_str += f"?{ebnf_rule}"
            else:
                rule_str += f" {ebnf_rule}"
        if t.ttype == RuleTokenType.MOD:
            if len(t.val) > 1:
                pass
            else:
                rule_str += t.val
        if t.ttype == RuleTokenType.AND:
            rule_str += " " + t.val
        if t.ttype == RuleTokenType.OR:
            rule_str += " " + t.val
        if t.ttype == RuleTokenType.ASSIGN:
            rule_str += ":"
        if t.ttype == RuleTokenType.STRING:
            rule_str += " " + t.val
        if t.ttype == RuleTokenType.PATTERN:
            if i+1 < len(tokens) and tokens[i+1].ttype == RuleTokenType.MOD:
                mod = tokens[i+1].val
                rule_item_str = " ( /" + t.val + "/ )"
                if mod.startswith("{") and mod.endswith("}"):
                    # We need to re-write the {min,max} pattern into a *, ? or + pattern
                    if mod[1:-1].isdigit():
                        mod = "{" + mod[1:-1] + "," + mod[1:-1] + "}"

                    start, stop = mod[1:-1].split(",")
                    start, stop = int(start), int(stop)
                    assert stop != 0
                    if start == 0 and stop == 1:
                        rule_str += rule_item_str + "?"
                    else:
                        for i in range(stop):
                            if start == 1 and i == 0:
                                rule_str += rule_item_str
                            else:
                                rule_str += rule_item_str + "?"
                else:
                    rule_str += rule_item_str + mod
                skip = True
            else:
                rule_str += " /" + t.val + "/"
    return rule_str

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Convert GBNF to EBNF')
    parser.add_argument('input', type=str, help='Input file path')
    parser.add_argument('output', type=str, help='Output file path')
    args = parser.parse_args()

    with open(args.input, "r") as f0:
        with open(args.output, "w") as f1:
            for l in f0.readlines():
                if l.strip():
                    f1.write(rule_gbnf_to_ebnf(l) + "\n")