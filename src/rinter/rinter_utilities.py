__package__='rinter.rinter_utilities'
r"""
Utilities for rinter.
"""

import re

BLOCK = '\{[^\}]*\}'
PAREN = '\([^\)]*\)'
COMMENT = re.compile('\/\*+[\s\S]*?\*\/')
INLINE_COMMENT = re.compile('\/\/[^\n]*')
FUNCTION_START = re.compile('\w+\s+\w+' + PAREN + '\s*\{')
FUNCTION_PROTOTYPE = re.compile('\w+\s+\w+' + PAREN + ';')
OPERATORS = '\+\-\/\*\(\)\%\~\|\^\&\<\>\?\:'
VARIABLE_DECLARATION = re.compile('\w+[\*\s]+\w+[\,\s\w]{0,80}=?[\w\s\d' +
    OPERATORS + ']{0,100};')
WHITESPACE = re.compile('\s?')
STRUCT = re.compile('struct\s+\w+\s?' + BLOCK + '[^\;]*\;')
DEFINE_STRUCT = re.compile('define\s+' + STRUCT.pattern)
IF_WITH_CURL = re.compile('if[\s\w]*' + PAREN + '[\s]*\{')
IF_SANS_CURL = re.compile('if[\s]*' + PAREN + '[^\{]*?\;\s*?')
ELSE_IF_WITH_CURL = re.compile('else\s+\{')
ELSE_IF_SANS_CURL = re.compile('else\s+' + IF_SANS_CURL.pattern + '\s?')
ELSE_WITH_CURL = re.compile('else\s?\{')
ELSE_SANS_CURL = re.compile('else\s+[^\;]*\;')
FOR = re.compile('for\s+' + PAREN + '\s?{')

# regex from pep8:
#   https://github.com/pycqa/pep8
EXTRANEOUS_WHITESPACE_REGEX = re.compile(r'[[({] | []}),;:]')


class Custom_SRE_Match(object):

    def __init__(self, g=None, s=None):
        self.g = g
        self.s = s

    def group(self):
        return self.g

    def span(self):
        return self.s


def load_file(filename):
    """ Loads a file in the format necessary for parsing """
    with open(filename, 'r') as fin:
        lines = fin.readlines()
    return ''.join(lines)


def parse_lines(program):
    """ Parses the given program into functions, main, comments, spaces,
    globals, includes, and defines """
    parsed = dict()

    parsed['comments'] = [ a for a in re.finditer(COMMENT, program)]
    parsed['prototypes'] = [a for a in re.finditer(FUNCTION_PROTOTYPE, program)]
    parsed['conditionals'] = parse_ifs(program)
    parsed['functions'] = parse_functions_with_bodies(f)

    return parsed


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
            return Custom_SRE_Match(first.group() + s.group(),
                   (first.span()[0], s.span()[1]))
    return Custom_SRE_Match(first.group(), first.span())

def glue_backward(second, first_list):
    """ Given a second SRE match, find an SRE match in first_list which
        ends where the second starts.  If found, return (group, span), else
        return the (group, span) for the second."""
    i = second.span()[0]
    for f in first_list:
        if f.span()[1] == i:
            return Custom_SRE_Match(f.group() + second.group(),
                    (f.span()[0], second.span()[1]))
    return Custom_SRE_Match(second.group(), second.span())

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
        start = possf.span()[0]

        fs = find_function_start(line[start:])
        if fs is None:
            continue

        end = parse_block(line, start+fs[1])[1]
        yield Custom_SRE_Match(line[start:end], (start, end))

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

def parse_structs(line):
    """ Return a tuple contaiting the SRE match objects of structs. """
    ret = [a for a in re.finditer(DEFINE_STRUCT, line)]
    l2 = replace_given_ranges(line, [a.span() for a in ret])
    ret += [a for a in re.finditer(STRUCT, l2)]
    return ret

def complete_blocks(line, l):
    """ Given a list of Custome_SRE_Match (with a '{' at the end of their
        groups, return the list with items extended to include their entire
        blocks.) """
    ret = list()
    for i in l:
        a = i.span()[0]
        b = parse_block(line, i.span()[1]-1)[1]
        spaces_after = re.match(re.compile('\s?'), line[b+1:])
        if spaces_after:
            b += spaces_after.span()[1]+1
        ret.append(Custom_SRE_Match(line[a:b], (a, b)))
    return ret

def parse_ifs(line):
    """ Return a tuple containing Custom_SRE_Match objects of ifs. """
    ei = [a for a in re.finditer(ELSE_IF_WITH_CURL, line)]
    ei = complete_blocks(line, ei)
    ei += [a for a in re.finditer(ELSE_IF_SANS_CURL, line)]
    l2 = replace_given_ranges(line, [a.span() for a in ei])
    i = [a for a in re.finditer(IF_WITH_CURL, l2)]
    i = complete_blocks(l2, i)
    i += [a for a in re.finditer(IF_SANS_CURL, l2)]
    e = [a for a in re.finditer(ELSE_WITH_CURL, l2)]
    e = complete_blocks(l2, e)
    e += [a for a in re.finditer(ELSE_SANS_CURL, l2)]
    for a in range(len(i)):
        i[a] = glue_forward(i[a], ei)
    for a in range(len(i)):
        i[a] = glue_forward(i[a], e)
    return i

def function_name_from_body(line):
    """ Given a function declaration, give the name of the function. """
    func_regex = re.compile('(\w+)\s?\(')
    return re.findall(func_regex, line)[0]


def parse_function_blocks(line):
    """ Return all function blocks in line. """
    funcs = parse_functions_with_bodies(line)
    ret = []
    for func in funcs:
        i = line.find('{', func.span()[0], func.span()[1])
        ret.append(parse_block(line, i))
    return ret

def parse_function_block(line, span):
    """ Return the block in the given span. """
    i = line.find('{', span[0], span[1])
    return parse_block(line, i)

def find_all_comments(line, span=None):
    """ Find all block and inline comments in the span. """
    if span is None:
        span = (0, len(line))
    ret = list()
    bc_gen = re.finditer(COMMENT, line[span[0]:span[1]])
    ic_gen = re.finditer(INLINE_COMMENT, line[span[0]:span[1]])
    for block_comment in bc_gen:
        rmin, rmax = block_comment.span()
        rmin += span[0]
        rmax += span[0]
        ret.append((rmin, rmax))
    for inline_comment in ic_gen:
        rmin, rmax = inline_comment.span()
        rmin += span[0]
        rmax += span[0]
        ret.append((rmin, rmax))
    ret.sort()
    return ret

def parse_fors(line):
    pass
