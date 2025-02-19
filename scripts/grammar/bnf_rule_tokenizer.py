import re
from enum import Enum

class RuleTokenType(Enum):
    STRING = "str"
    OR = "or"
    AND = "and"
    MOD = "mod"
    PATTERN = "ptr"
    ASSIGN = "assign"
    RULE = "rule"

class RuleToken:
    def __init__(self, val: str, ttype: RuleTokenType):
        self.val = val
        self.ttype = ttype

    def is_closing(self):
        return self.ttype == RuleTokenType.AND and self.val == ")"

    def __repr__(self):
        return f"<Token {self.ttype.name}: {repr(self.val)}>"

ALLOWED_RULE_CHARS = re.compile(r'[a-zA-Z0-9\-_]')
def tokenize_rule(expr: str, ttype: RuleTokenType = None):
    if ttype is None:
        # Peek next char
        expr = expr.lstrip()
        if not expr:
            return
        char = expr[0]
        if char == '"':
            yield from tokenize_rule(expr, RuleTokenType.STRING)
        elif char == "|" :
            yield from tokenize_rule(expr, RuleTokenType.OR)
        elif char in ["(", ")"]:
            yield from tokenize_rule(expr, RuleTokenType.AND)
        elif char == "{" or char in ["?", "*", "+"]:
            yield from tokenize_rule(expr, RuleTokenType.MOD)
        elif char == "[":
            yield from tokenize_rule(expr, RuleTokenType.PATTERN)
        elif char == ":":
            yield from tokenize_rule(expr, RuleTokenType.ASSIGN)
        else:
            yield from tokenize_rule(expr, RuleTokenType.RULE)
        return

    elif ttype == RuleTokenType.STRING:
        # parse string
        token, expr = expr[0], expr[1:]
        assert token == '"'

        escaping = False
        while True:
            char, expr = expr[0], expr[1:]
            token += char
            if not escaping and char == '"':
                # terminal char
                break
            elif not escaping and char == '\\':
                escaping = True
            elif escaping:
                escaping = False
        yield RuleToken(token, ttype)
        yield from tokenize_rule(expr, ttype=None)
    elif ttype == RuleTokenType.MOD:
        token, expr = expr[0], expr[1:]
        assert token in ["*", "{", "?", "+"]

        if token in ["*", "?", "+"]:
            pass
        else:
            # We can just look for the closing } without escape mechanism
            split_at = expr.index("}") + 1
            token += expr[:split_at]
            expr = expr[split_at:]
        yield RuleToken(token, ttype)
        yield from tokenize_rule(expr, ttype=None)
    elif ttype == RuleTokenType.RULE:
        token = ''
        while True:
            if not expr:
                break
            char, expr = expr[0], expr[1:]
            if ALLOWED_RULE_CHARS.match(char):
                token += char
            else:
                expr = char + expr
                break
        if token:
            yield RuleToken(token, RuleTokenType.RULE)
        yield from tokenize_rule(expr, ttype=None)
    elif ttype == RuleTokenType.OR:
        token, expr = expr[0], expr[1:]
        assert token == "|"
        yield RuleToken(token, ttype)
        yield from tokenize_rule(expr, ttype=None)
    elif ttype == RuleTokenType.AND:
        token, expr = expr[0], expr[1:]
        assert token in ["(", ")"]
        yield RuleToken(token, ttype)
        yield from tokenize_rule(expr, ttype=None)
    elif ttype == RuleTokenType.PATTERN:
        # parse pattern till unescaped ] char
        token, expr = expr[0], expr[1:]
        assert token == '['

        escaping = False
        while True:
            char, expr = expr[0], expr[1:]
            token += char
            if not escaping and char == ']':
                # terminal char
                break
            elif not escaping and char == '\\':
                escaping = True
            elif escaping:
                escaping = False

        yield RuleToken(token, ttype)
        yield from tokenize_rule(expr, ttype=None)
    elif ttype == RuleTokenType.ASSIGN:
        assert expr.startswith("::=")
        token = expr[:3]
        expr = expr[3:]
        yield RuleToken(token, ttype)
        yield from tokenize_rule(expr, ttype=None)
    else:
        raise ValueError(f"Unimplemented tokenizer for {ttype}")
