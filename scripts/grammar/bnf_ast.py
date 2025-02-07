from typing import List, Tuple, Dict, Optional, Union
from functools import reduce
from textwrap import indent

from bnf_rule_tokenizer import RuleToken, RuleTokenType, tokenize_rule

def ebnf_name_normalize(name: str) -> str:
    if name == "root":
        return "start"
    return name.replace("-", "_").lower()

def ebnf_mod_repeat(ebnf_rule: str, mod: str) -> str:
    if mod is None: return ebnf_rule

    import re
    if mod in ["*", "+", "?"]:
        return f"{ebnf_rule}{mod}"
    else:
        single_match = re.match(r"{([0-9]+)}", mod)
        range_match = re.match(r"{([0-9]+),([0-9]+)}", mod)

        if single_match:
            # just repeat n times
            return " ".join([ ebnf_rule for _ in range(int(single_match.group(1))) ])

        elif range_match:
            # repeat between n and m times
            min_repeats = int(range_match.group(1))
            max_repeats = int(range_match.group(2))

            rule_out = " ".join([ ebnf_rule for _ in range(int(range_match.group(1))) ])
            for _ in range(max_repeats - min_repeats):
                rule_out += f" {ebnf_rule}?"

            return rule_out
        else:
            raise ValueError(f"Invalid mod {mod}")

class Node:
    pass

class OrInnerNode(Node):
    def __init__(self, children):
        self.children = children

    def __repr__(self):
        children: str = ([ indent(repr(c), " " * 5) for c in self.children ])
        for i, c in enumerate(children):
                children[i] = " ->| " + children[i][5:]
        children_str = "\n".join(children)

        return f"<OrInnerNode: {len(self.children)}x entries\n{children_str}\n/>"

    def to_bnf(self):
        return "( " + (" | ".join([ c.to_bnf() for c in self.children ])) + " )"

    def to_ebnf(self):
        return "(" + (" | ".join([ c.to_ebnf() for c in self.children ])) + ")"

    def get_leftmosts(self):
        return reduce(lambda x,y: x+y, [ c.get_leftmosts() for c in self.children ])

    def get_rule_names(self) -> List[str]:
        return reduce(lambda x,y: x+y, [ c.get_rule_names() for c in self.children ])



class SequenceNode(Node):
    def __init__(self, children, mod, explicit: bool = True):
        self.children = children
        self.mod = mod
        self.explicit = explicit

    def __repr__(self):
        children: str = ([ indent(repr(c), " " * 5) for c in self.children ])
        for i, c in enumerate(children):
                children[i]= " ->& " + children[i][5:]
        children_str = "\n".join(children)
        return f"<SequenceNode: {len(self.children)}x entries{'' if self.explicit else ', implicit'}{'' if not self.mod else ' ' + self.mod}\n{children_str}\n/>"

    def to_bnf(self):
        assert self.explicit or (not self.explicit and self.mod is None)
        elements_str = ' '.join([ c.to_bnf() for c in self.children ])
        if not self.explicit:
            assert self.mod is None
            return f"{elements_str}"
        else:
            return f"( {elements_str} ){self.mod if self.mod else ''}"

    def to_ebnf(self):
        assert self.explicit or (not self.explicit and self.mod is None)
        elements_str = ' '.join([ c.to_ebnf() for c in self.children ])
        if self.explicit or self.mod is not None:
            elements_str = '( ' + elements_str + ' )'
        if not self.explicit:
            assert self.mod is None
            return elements_str
        else:
            return ebnf_mod_repeat(elements_str, self.mod)

    def get_leftmosts(self):
        return self.children[0].get_leftmosts()

    def get_rule_names(self) -> List[str]:
        return reduce(lambda x,y: x+y, [ c.get_rule_names() for c in self.children ])

class RuleNode(Node):
    def __init__(self, name, mod):
        self.name = name
        self.mod = mod

    def __repr__(self):
        return f"<RuleNode: {self.name} {self.mod if self.mod else ''}>"

    def to_bnf(self):
        return f"{self.name}{self.mod if self.mod else ''}"

    def to_ebnf(self):
        normalized_name = ebnf_name_normalize(self.name)
        return ebnf_mod_repeat(normalized_name, self.mod)

    def get_leftmosts(self):
        return [ self ]

    def get_rule_names(self) -> List[str]:
        return [ self.name ]

class PatternTerminalNode(Node):
    def __init__(self, pattern, mod):
        self.pattern = pattern
        self.mod = mod

    def __repr__(self):
        return f"<PatternNode: {self.pattern} {self.mod if self.mod else ''}>"

    def to_bnf(self):
        return f"{self.pattern}{self.mod if self.mod else ''}"

    def to_ebnf(self):
        normalized_pattern = f"( /{self.pattern}/ )"
        return ebnf_mod_repeat(normalized_pattern, self.mod)

    def get_leftmosts(self):
        return [ self ]

    def get_rule_names(self) -> List[str]:
        return [ ]

class DirectTerminalNode(Node):
    def __init__(self, value, mod):
        self.value = value
        self.mod = mod

    def __repr__(self):
        return f"<TerminalNode: {self.value} {self.mod if self.mod else ''}>"

    def to_bnf(self):
        return f'{self.value}{self.mod if self.mod else ""}'

    def to_ebnf(self):
        return ebnf_mod_repeat(self.value, self.mod)

    def get_leftmosts(self):
        return [ self ]

    def get_rule_names(self) -> List[str]:
        return [ ]

def parse_rule(tokens: List[RuleToken]) -> Tuple[str, Node]:
    assert len(tokens) >= 3
    assert tokens[0].ttype == RuleTokenType.RULE
    assert tokens[1].ttype == RuleTokenType.ASSIGN
    lhs = tokens[0]
    rhs = tokens[2:]
    return lhs.val, parse_rhs(rhs)

def parse_rhs(tokens: List[RuleToken]) -> Node:
    assert RuleTokenType.ASSIGN not in [ t.ttype for t in tokens if isinstance(t, RuleToken) ]
    # Transform inner token sequences as atomic item
    items = _resolve_sequence(tokens)

    is_or = RuleTokenType.OR in [ t.ttype for t in items if isinstance(t, RuleToken) ]
    is_single = len(items) == 1 or (len(items) == 2 and isinstance(items[1], RuleToken) and items[1].ttype == RuleTokenType.MOD)

    if is_single:
        # Single item
        has_mod = len(items) == 2 and items[1].ttype == RuleTokenType.MOD
        single_item = items[0]
        if isinstance(single_item, RuleToken):
            if single_item.ttype == RuleTokenType.RULE:
                return RuleNode(single_item.val, items[1].val if has_mod else None)
            elif single_item.ttype == RuleTokenType.STRING:
                return DirectTerminalNode(single_item.val, items[1].val if has_mod else None)
            elif single_item.ttype == RuleTokenType.PATTERN:
                return PatternTerminalNode(single_item.val, items[1].val if has_mod else None)
            else:
                raise ValueError(f"Unexpected token type {single_item.ttype}")
        elif isinstance(single_item, list):
            assert isinstance(single_item[0], RuleToken) and single_item[0].ttype == RuleTokenType.AND and single_item[0].val == "("
            assert isinstance(single_item[-1], RuleToken) and single_item[-1].ttype == RuleTokenType.AND and single_item[-1].val == ")"
            inner_seq = single_item[1:-1]
            seq_obj = parse_rhs(inner_seq)
            seq_obj.mod = items[1].val if has_mod else None
            seq_obj.explicit = True
            return seq_obj
        else:
            raise ValueError(f"Unexpected item type {type(single_item)}")
    elif is_or:
        # a | b | c
        # -> split into [a, b, c]
        or_elements = []
        or_start = 0
        i = 0
        n_items = len(items)
        while i < n_items:
            item = items[i]
            if isinstance(item, RuleToken) and item.ttype == RuleTokenType.OR:
                or_elements.append(
                    items[or_start:i]
                )
                i += 1
                or_start = i
            else:
                i += 1
        or_elements.append(
            items[or_start:i]
        )

        #assert 0 not in [ len(or_item) for or_item in or_elements ], repr(or_elements) + "\n" + repr(items)

        # resolve recursively
        inner_items = [ parse_rhs(or_item) for or_item in or_elements ]

        return OrInnerNode(inner_items)
    else:
        # a b c d e
        # Sequence without (non-inner) OR elements
        seq_elements = []
        n_items = len(items)
        i = 0
        while i < n_items:
            item = items[i]

            if n_items > i + 1 and isinstance(items[i+1], RuleToken) and items[i+1].ttype == RuleTokenType.MOD:
                # The current item has a mod
                seq_elements.append(
                    parse_rhs(items[i:i+2])
                )
                i += 2
            elif isinstance(item, RuleToken):
                # The current item has no mod
                seq_elements.append(parse_rhs(items[i:i+1]))
                i += 1
            elif isinstance(item, list):
                # The current item is an inner sequence
                seq_elements.append(parse_rhs(items[i:i+1]))
                i += 1
            else:
                raise ValueError(f"Unexpected item type {type(item)}")

        return SequenceNode(seq_elements, None, explicit=False)

def _resolve_sequence(tokens: List[RuleToken]) -> List[Union[RuleToken, List[RuleToken]]]:
    base_items = []
    i = 0
    n_tokens = len(tokens)
    while i < n_tokens:
        token = tokens[i]
        if isinstance(token, RuleToken) and token.ttype == RuleTokenType.AND and token.val == "(":
            closing_idx = _find_closing_seq_token(tokens[i+1:]) + 1
            # We have an inner sequence at: tokens[i:i+closing_idx+1]
            # -> Check if the inner sequence is the actual sequence
            if i == 0 and closing_idx + 1 == n_tokens:
                # The inner sequence is the actual sequence
                return tokens
            else:
                inner_seq = tokens[i:i+closing_idx+1]
                base_items.append(_resolve_sequence(inner_seq))
            i = i+closing_idx+1
        else:
            base_items.append(token)
            i += 1
    return base_items

def _find_closing_seq_token(tokens: List[RuleToken], __acc: int = 0,__depth: int = 0) -> int:
    if not tokens:
        raise ValueError(f"Could not find closing sequence token")
    ctoken, *rest = tokens

    is_closing = isinstance(ctoken, RuleToken) and ctoken.ttype == RuleTokenType.AND and ctoken.val == ")"
    is_opening = isinstance(ctoken, RuleToken) and ctoken.ttype == RuleTokenType.AND and ctoken.val == "("

    if is_closing and __depth == 0:
        return __acc
    elif is_closing:
        return _find_closing_seq_token(rest, __acc + 1, __depth - 1)
    elif is_opening:
        return _find_closing_seq_token(rest, __acc + 1, __depth + 1)
    else:
        return _find_closing_seq_token(rest, __acc + 1, __depth)

def build_graph(rules):
    graph = {}
    for rule in rules:
        rule_tokens = list(tokenize_rule(rule))
        lhs, rhs = parse_rule(rule_tokens)
        if lhs not in graph:
            graph[lhs] = rhs
        else:
            raise ValueError(f"Duplicate rule {lhs}")
    return graph

def eliminate_left_recursion(graph: Dict[str, Node]) -> Dict[str, Node]:
    """
    Eliminates left recursion in the BNF graph.
    Handles both direct and indirect left recursion.
    """
    def is_left_recursive(lhs: str, rhs: Node) -> bool:
        leftmosts = rhs.get_leftmosts()
        is_left_rec = any(isinstance(leftmost, RuleNode) and leftmost.name == lhs for leftmost in leftmosts)
        if is_left_rec:
            print("Found left recursion for rule", lhs)
        else:
            print("No left recursion for rule", lhs)
        return is_left_rec

    def process_direct_left_recursion(lhs: str, rhs: OrInnerNode):
        """
        Eliminates direct left recursion for a single rule `lhs`.
        """
        non_recursive_parts = []
        recursive_parts = []

        for child in rhs.children:
            if isinstance(child, SequenceNode) and isinstance(child.children[0], RuleNode) and child.children[0].name == lhs:
                # It's recursive
                recursive_parts.append(SequenceNode(child.children[1:], None, explicit=False))
            else:
                # It's not recursive
                non_recursive_parts.append(child)

        if not recursive_parts:
            # No direct left recursion
            return rhs

        # Create the transformed rules
        new_non_terminal = f"{lhs}_rec"

        # A -> non_recursive_parts new_non_terminal
        new_non_recursive = OrInnerNode(
            [SequenceNode([child, RuleNode(new_non_terminal, None)], None, explicit=False) for child in non_recursive_parts]
        )

        # new_non_terminal -> recursive_parts new_non_terminal | ε
        new_recursive = OrInnerNode(
            [SequenceNode(child.children + [RuleNode(new_non_terminal, None)], None, explicit=False) for child in recursive_parts] +
            [DirectTerminalNode("ε", None)]
        )

        return new_non_recursive, new_recursive, new_non_terminal

    non_terminals = list(graph.keys())
    for i, lhs in enumerate(non_terminals):
        # Resolve indirect left recursion
        for j in range(i):
            rhs = graph[lhs]
            if isinstance(rhs, OrInnerNode):
                new_rhs_children = []
                for child in rhs.children:
                    if isinstance(child, SequenceNode) and isinstance(child.children[0], RuleNode) and child.children[0].name == non_terminals[j]:
                        # Replace A -> B γ with B's RHS
                        replacement_rhs = graph[non_terminals[j]]
                        if isinstance(replacement_rhs, OrInnerNode):
                            new_rhs_children.extend(
                                [SequenceNode(replacement.children + child.children[1:], None, explicit=False)
                                 for replacement in replacement_rhs.children]
                            )
                        else:
                            new_rhs_children.append(child)
                    else:
                        new_rhs_children.append(child)
                graph[lhs] = OrInnerNode(new_rhs_children)

        # Resolve direct left recursion
        rhs = graph[lhs]
        if isinstance(rhs, OrInnerNode) and is_left_recursive(lhs, rhs):
            new_rhs, new_rec_rhs, new_non_terminal = process_direct_left_recursion(lhs, rhs)
            graph[lhs] = new_rhs
            graph[new_non_terminal] = new_rec_rhs

    return graph

if __name__ == "__main__":
    rule = '''Address-line ::= "[" space (Address-line-item ("," space Address-line-item)*)? "]" space'''
    #rule = '''root ::= alternative-0 | alternative-1 '''
    tokens = list(tokenize_rule(rule))
    lhs, rhs = parse_rule(tokens)

    print(lhs)
    print(rhs)

    with open("scripts/fhir_grammar.gbnf", "r") as f:
        rules = [ l for l in f.readlines() if l.strip() ]
    # rules = [
    #     "A ::= C a | b",
    #     "B ::= C b | c",
    #     "C ::= A"
    # ]
    graph = build_graph(rules)

    # Write EBNF out
    with open("scripts/fhir_grammar2.ebnf", "w") as f:
        f.write("\n".join( "?{}: {}".format(ebnf_name_normalize(k), v.to_ebnf()) for k, v in graph.items() ))

    # find the root node
    root_node = "root"
    root_rhs = graph[root_node]
    #print("\n".join( "{} ::= {}".format(k, v.to_bnf()) for k, v in graph.items() ))
    #graph_new = eliminate_left_recursion(graph)
    #print("\n".join( "{} ::= {}".format(k, v.to_bnf()) for k, v in graph_new.items() ))






