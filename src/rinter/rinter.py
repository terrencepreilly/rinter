__package__='rinter.rinter'
"""
Utility to check for formatting heresy, as defined by the High Priest
of the Eighth Day of our Lord.

Among the items checked by rinter:
    * File contains header with name, section, assignment #, due date,
      and total points in the following format:
        /*
           Name: ********* *********
           Section: #########
           Assignment: **************
           Due Date: ****(*****) (#)#, ####
           Credit: ## points

           Problem: ***** **** ...

           Solution: ***** **** ...

           Errors handled: ****** ****...

           Limitations: ****** ****...

           (Acknowledgement: ***** ****...)

    * Comments are present before each function, and do not occur in the
      body of a function.
    * All lines are under 80 characters long.
    * Function prototypes occur only inside of functions, and not in global
      scope.
    * No function is more than 25 lines in length.
    * Two blank lines before each function.
    * Indentation level of 3 spaces
    * Alphabetic declaration of variables
    * No mixing of case in variables and constants
    * Constants defined all upper case.
"""
import argparse
import re

from rinter.rinter_utilities import *

REQUIRED_HEADER_SECTIONS = [
    'Name',
    'Section',
    'Assignment',
    'Due',
    'Credit',
    'Problem',
    'Solution',
    'Errors handled',
    'Limitations'
    ]
INDENTATION_LEVEL = re.compile(' {3}')


def get_file_header(line):
    """ Return the SRE_Match object corresponding to the header, if it exists.
        Otherwise, return None. """
    phead = None
    comments = re.finditer(COMMENT, line)
    try:
        phead = next(comments)
    except StopIteration as e:
        phead = None
    return phead


def file_contains_header(line):
    """ Return True if the file contains a comment at the start of the
    the file, where the comment is not associated with a function."""
    header = get_file_header(line)
    if header is None:
        return False

    function_gen = parse_functions_with_bodies(line)
    first_function = None
    try:
        first_function = next(function_gen)
    except StopIteration as e:
        return True

    if first_function.span()[0] <= header.span()[0]:
        return False
    return True


def header_contains_necessary_fields(header):
    """ Return a list of strings describing the missing headers. """
    lines = header.split('\n')
    ret = []
    for hsec in REQUIRED_HEADER_SECTIONS:
        f = filter(lambda x : x.lstrip().startswith(hsec), lines)
        try:
            next(f)
        except:
            ret.append('header missing {}'.format(hsec))
    return ret


def all_lines_eighty_characters(line):
    """ Return list of lines over eighty characters """
    ret = list()
    newlines = re.finditer(re.compile('\n'), line)
    prev = 0
    for newline in newlines:
        if newline.span()[0] - prev > 80:
            ret.append(
                'Line over eighty characters {}'.format(newline.span()[0]))
        prev = newline.span()[1]
    return ret


def no_global_functions(line):
    funcs = parse_functions_with_bodies(line)
    ranges = [a.span() for a in funcs]
    line2 = replace_given_ranges(line, ranges)
    ret = []
    for proto in re.finditer(FUNCTION_PROTOTYPE, line2):
        ret.append('Global function prototype {}'.format(proto.span()[0]))
    return ret


def two_lines_before_functions(program):
    ss = re.compile('\s{2,}')
    blanks = re.finditer(ss, program)
    blanks = filter(lambda x : x.group().count('\n') >= 2, blanks)
    blanks = [a for a in blanks]
    funcs = parse_functions_with_bodies(program)
    ret = list()
    for func in funcs:
        f = glue_backward(func, blanks)
        if f.group() == func.group():
            ret.append(
                'Not two lines before function {}'.format(func.span()[0]))
    return ret


def indentation_level_three_spaces(line):
    pass


def comment_before_function(program):
    funcs = find_function_or_comment(program)
    l = list()
    for func in funcs:
        if not re.match(COMMENT, func.group()):
            func_name = function_name_from_body(func.group())
            l.append('Function {} missing documentation'.format(func_name))
    return l

def comments_within_functions(program):
    functions = parse_function_blocks(program)
    ret = list()
    for func in functions:
        comms = find_all_comments(program, func)
        for comment in comms:
            ret.append('Comment within function {}'.format(comment[0]))
    return ret


def functions_twenty_five_lines(program):
    NEWLINE = re.compile('\n')
    bfuncs = parse_functions_with_bodies(program)
    ret = list()
    for bfunc in bfuncs:
        block = parse_function_block(program, bfunc.span())
        if len(re.findall(NEWLINE, program[block[0]:block[1]])) > 25:
            fname = function_name_from_body(bfunc.group())
            message = 'Function {} more than 25 lines {}'
            ret.append(message.format(fname, bfunc.span()[0]))
    return ret


def error_list(program):
    l = list()
    if file_contains_header(program):
        header = get_file_header(program)
        l = header_contains_necessary_fields(header.group())
    else:
        l.append('File header missing.')

    l.extend(comment_before_function(program))
    l.extend(all_lines_eighty_characters(program))
    l.extend(no_global_functions(program))
    l.extend(two_lines_before_functions(program))
    l.extend(comments_within_functions(program))
    l.extend(functions_twenty_five_lines(program))
    return l


def _main():
    parser = argparse.ArgumentParser(description='Lint utility for CPS360.')

    parser.add_argument('-f', nargs='?', help='The filename for the program')

    args = parser.parse_args()

    if args.f:
        program = load_file(args.f)
        l = error_list(program)
        l.sort()
        print('\n'.join(l))
