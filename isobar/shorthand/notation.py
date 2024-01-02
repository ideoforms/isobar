import re
from ..pattern.sequence import PSequence

def _parser_push(obj, sequence: PSequence, depth: int):
    """
    Append an item to the (possibly nested) PSequence.
    """
    while depth > 0:
        # Iterate up the stack
        sequence = sequence[-1]
        depth -= 1

    sequence.sequence.append(obj)

def _parser_get_next_token(string: str):
    """
    Return the next token in the string.
    This may be a number (integer/float) or a note name (e.g. c#4).
    """
    note_pattern = r"(-?[0-9]+(\.[0-9]+)?|[a-g]#?[0-9])\b"
    if string[0] in '[]':
        return string[0]
    else:
        match = re.match(note_pattern, string)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid character in notation: %s" % string)

def _parser_token_to_value(token: str):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token

def parse_notation(string: str):
    """
    Parses a string into a (possibly nested) PSequence.
    For example:

        parse_notation('1 2 [10 11] [20 [30 31 32]]')

    results in

        seq([1, 2, seq([10, 11]), seq([20, seq([30, 31, 32])])])])

    Implementation of a push-down automaton, thanks to:
    Source: https://stackoverflow.com/questions/4284991/parsing-nested-parentheses-in-python-grab-content-by-level
    """
    groups = PSequence([])
    depth = 0

    try:
        while True:
            token = _parser_get_next_token(string)
            if token == '[':
                _parser_push(PSequence([]), groups, depth)
                depth += 1
            elif token == ']':
                depth -= 1
            else:
                value = _parser_token_to_value(token)
                _parser_push(value, groups, depth)

            string = string[len(token):]
            string = string.lstrip()

            if len(string) == 0:
                break
    except IndexError:
        raise ValueError('Notation error: parenthesis mismatch')

    if depth > 0:
        raise ValueError('Notation error: parenthesis mismatch')
    else:
        return groups

if __name__ == "__main__":
    seq = parse_notation('1 2 [10 11] [c#4 [30.1 30.2 30.3]]')
    expected = [1, 2, 10, 'c#4', 1, 2, 11, 30.1, 1, 2, 10, 'c#4', 1, 2, 11, 30.2]
    print(seq.nextn(16))