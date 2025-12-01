import copy
import re
from ..pattern import PSequence, PStutter, PSkip

def _parser_push(obj, sequence: PSequence, depth: int):
    """
    Append an item to the (possibly nested) PSequence.
    """
    tip = _parser_get_current_tip(sequence, depth)
    tip.sequence.append(obj)

def _parser_get_current_tip(sequence: PSequence, depth: int):
    for n in range(depth):
        sequence = sequence[-1]
    return sequence

def _parser_get_next_token(string: str):
    """
    Return the next token in the string.
    This may be:
     - a number (integer/float)
     - a note name (e.g. c#4)
     - a rest (- or ~)
     - a repetition operator (!)
     - a chance operator (?)
    """
    note_pattern = r"((-?[0-9]+(\.[0-9]+)?)|([a-g]#?[0-9])|[\~-])"
    if string[0] in '[]!?':
        return string[0]
    else:
        match = re.match(note_pattern, string)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid character in notation: %s" % string)

def _parser_token_to_value(token: str):
    if token in ["~", "-"]:
        return None

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
                string = string[1:].lstrip()
            elif token == ']':
                depth -= 1
                string = string[1:].lstrip()
            elif token == '!':
                # Repetition operator.
                # The next token must be an integer indicating the number of repetitions.
                string = string[1:]
                if len(string) == 0:
                    raise ValueError("Notation error: expected number after '!'")
                
                count_token = _parser_get_next_token(string)
                string = string[len(count_token):].lstrip()

                try:
                    count = int(count_token)
                except ValueError:
                    raise ValueError("Notation error: expected integer after '!', got %s" % count_token)

                current_sequence = _parser_get_current_tip(groups, depth)
                last_item = current_sequence.sequence[-1]
                for n in range(count - 1):
                    current_sequence.sequence.append(copy.copy(last_item))

            elif token == '?':
                # Chance operator.
                # The next token may be skipped with a random probability, 0.5 by default.
                string = string[1:].lstrip()
                probability = 0.5
                
                if len(string) > 0 and string[0] in "0123456789-.":
                    prob_token = _parser_get_next_token(string)
                    try:
                        probability = float(prob_token)
                    except ValueError:
                        raise ValueError("Notation error: expected integer after '!', got %s" % count_token)
                    string = string[len(prob_token):].lstrip()

                current_sequence = _parser_get_current_tip(groups, depth)
                last_item = current_sequence.sequence.pop(-1)                
                current_sequence.sequence.append(PSkip(last_item, probability))
            else:
                value = _parser_token_to_value(token)
                _parser_push(value, groups, depth)
                string = string[len(token):].lstrip()

            if len(string) == 0:
                break
    except IndexError:
        raise ValueError('Notation error: parenthesis mismatch')

    if depth > 0:
        raise ValueError('Notation error: parenthesis mismatch')
    else:
        return groups

if __name__ == "__main__":
    seq = parse_notation('1 2 ~ - [10 11] [c#4 [30.1 30.2 30.3]]')
    expected = [1, 2, None, None, 10, 'c#4', 1, 2, None, None, 11, 30.1, 1, 2, None, None, 10, 'c#4', 1, 2, None, None, 11, 30.2]
    print(seq.nextn(16))