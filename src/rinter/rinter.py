__package__='rinter.rinter'
"""
Utility to check for formatting heresy, as defined by the High Priest
of the Eighth Day of our Lord.

Among the items checked by rat_linter:
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
import re

from rinter.rinter_utilities import *

REQUIRED_HEADER_SECTIONS = [
    'Name',
    'Section',
    'Assignment',
    'Due Date',
    'Credit',
    'Problem',
    'Solution',
    'Errors handled',
    'Limitations'
    ]

def file_contains_header(line):
    """ Return True if file contains a comment block at the start. """
    comments = re.finditer(COMMENT, line)
    try:
        phead = next(comments)
    except StopIteration as e:
        return False
    if phead.span()[0] != 0:
        return False
    return True


def header_contains_necessary_fields(header):
    """ Return true if the given header contains all necessary fields,
        each on a new line, with the section headers first. """
    lines = header.split('\n')
    ret = []
    for hsec in REQUIRED_HEADER_SECTIONS:
        f = filter(lambda x : x.startswith(hsec), lines)
        try:
            next(f)
        except:
            ret.append('header missing ' + hsec)
    return ret or None


def all_lines_eighty_characters(line):
    """ Return False if any line is over eighty characters """
    newlines = re.finditer(re.compile('\n'), line)
    prev = 0
    for newline in newlines:
        if newline.span()[0] - prev > 80:
            return False
        prev = newline.span()[1]
    return True


def no_global_functions(line):
    funcs = parse_functions_with_bodies(line)
    ranges = [(a[1], a[2]) for a in funcs]
    line2 = replace_given_ranges(line, ranges)
    ret = []
    for proto in re.finditer(FUNCTION_PROTOTYPE, line2):
        ret.append('Global function prototype {}'.format(proto.span()[0]))
    return ret or None


def two_lines_before_functions(line):
    ss = re.compile('\s{2,}')
    blanks = re.finditer(ss, line)
    blanks = filter(lambda x : x.group().count('\n') >= 2, blanks)
    blanks = map(lambda x: x.span(), blanks)
    funcs = map( lambda x: (x[1], x[2]), parse_functions_with_bodies(line))
    ret = []
    for func in funcs:
        # see if it comes _immediately_ before a function
        has_two = False
        for blank in blanks:
            if blank[1] == func[0]:
                has_two = True
        if not has_two:
            ret.append('Two spaces before function {}'.format(func[0]))
    return ret or None
