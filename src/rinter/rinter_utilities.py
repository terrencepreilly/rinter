__package__='rinter.rinter_utilities'
r"""
Utilities for rinter.
"""

import re

COMMENT = re.compile('\/\*+[\s\S]*?\*\/')
FUNCTION_START = re.compile('\w+\s+\w+\([^\)]*\)\s*\{')
FUNCTION_PROTOTYPE = re.compile('\w+\s+\w+\([\s\S]*?\);')
OPERATORS = '\+\-\/\*\(\)\%\~\|\^\&\<\>\?\:'
VARIABLE_DECLARATION = re.compile('\w+[\*\s]+\w+[\,\s\w]{0,80}=?[\w\s\d' +
    OPERATORS + ']{0,100};')
WHITESPACE = re.compile('\s?')

# regex from pep8:
#   https://github.com/pycqa/pep8
EXTRANEOUS_WHITESPACE_REGEX = re.compile(r'[[({] | []}),;:]')
INDENT_REGEX = re.compile(r'([ \t]*)')


def load_file(filename):
    """ Loads a file in the format necessary for parsing """
    with open(filename, 'r') as fin:
        lines = fin.readlines()
    return ''.join(lines)


def parse_lines(program):
    """ Parses the given program into functions, main, comments, spaces,
    globals, includes, and defines """
    parsed = dict()

    dict['comments'] = re.findall(COMMENT, program)
    dict['prototypes'] = re.findall(FUNCTION_PROTOTYPE)

    return parsed


def _find_function_or_comment(line):
    """ Find instances of either comments and functions or just functions.
        Returns SRE_Match objects """
    pos_func_regex = re.compile('{}{}{}|{}'.format(
        COMMENT.pattern, WHITESPACE.pattern, FUNCTION_START.pattern,
        FUNCTION_START.pattern))
    return [a for a in re.finditer(pos_func_regex, line)]

def find_function_or_comment(line):
    """ Find instances of either comments and functions or just functions.
        Returns SRE_Match objects """
    pos_func_comments = re.compile('{}{}'.format(COMMENT.pattern,
                                                 WHITESPACE.pattern))
    pos_funcs = [a  for a in re.finditer(FUNCTION_START, line)]
    pos_comms = [a for a in re.finditer(pos_func_comments, line)]
    for i in range(len(pos_funcs)):
        pos_funcs[i] = glue_backward(pos_funcs[i], pos_comms)
    return pos_funcs

def glue_forward(first, second_list):
    """ Given a first SRE match, find an SRE match in the second list which
        starts where the first ends.  If found, return (group, span), else
        return the (group, span) for the first. """
    i = first.span()[1]
    for s in second_list:
        if s.span()[0] == i:
            return (first.group() + s.group(),
                    (first.span()[0], second.span()[1]))
    return first.group(), first.span()

def glue_backward(second, first_list):
    """ Given a second SRE match, find an SRE match in first_list which
        ends where the second starts.  If found, return (group, span), else
        return the (group, span) for the second."""
    i = second.span()[0]
    for f in first_list:
        if f.span()[1] == i:
            return (f.group() + second.group(),
                    (f.span()[0], second.span()[1]))
    return second.group(), second.span()

def find_function_start(line):
    """ Find the first start of a function. (Not a function prototype.) """
    fs_gen = re.finditer(FUNCTION_START, line)
    for function_start in fs_gen:
        return function_start.span()[0], function_start.span()[1]
    return None


def parse_block(line, start):
    """ Parse a block in line starting at index i. Return the indices of
        said block.  """
    i = start + 1
    count = 1
    while count > 0 and i < len(line):
        if line[i] == '{':
            count += 1
        elif line[i] == '}':
            count -= 1
        i += 1
    return (start, i)

def parse_functions_with_bodies(line):
    """ Return a generator which parses functions (with comments) from
    code. Returns as a tuple: (function, start index, end index)."""
    for possf in find_function_or_comment(line):
        start = possf[1][0]

        fs = find_function_start(line[start:])
        if fs is None:
            continue

        end = parse_block(line, start+fs[1])[1]
        yield (line[start:end], start, end)

def parse_variable_declarations(line):
    """ Return a list of variable declarations from the input.
        Doesn't check if the variable declaration is a parameter. """
    return re.findall(VARIABLE_DECLARATION, line)

def remove_given_ranges(line, ranges):
    """ Remove the given ranges from the line. """
    ranges.sort()
    start_cpy = 0
    ret = ''
    for r in ranges:
        ret += line[start_cpy:r[0]]
        start_cpy = r[1]+1
    ret += line[start_cpy:]
    return ret

def replace_given_ranges(line, ranges):
    """ Replaces the given ranges with spaces. """
    ret = str(line)
    for r in ranges:
        a = r[0]
        b = r[1] if r[1] < len(line) else len(line)-1
        ret = ret[:a] + ' '*(b-a+1) + ret[b+1:]
    return ret
