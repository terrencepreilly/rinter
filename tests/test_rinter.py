import unittest
from random import choice

from rinter.rinter import *
from rinter.rinter_utilities import *

class TestUtilityMethods(unittest.TestCase):

    def setUp(self):
        self.c = 'words words words /* comment */ words words'
        self.c_and_f = 'words /* comment */ int func(int b, int c) {aoth;}'
        self.p_and_c = 'void my_func(); /* a prototype */'
        self.p = 'word word word\nint a_func();\nword word'
        self.p_and_f = 'int func(void);\nvoid func2(int i) {\naoesnth;\n}\n'
        self.block = '{\nword word;\nif (cond) {\n\tsomething\n}{}\n}'
        self.embedded_block = 'word;\nword' + self.block + '\nblock;\n'

    def test_parse_block(self):
        b1 = parse_block(self.block, 0)
        b2 = parse_block(self.embedded_block, 10)
        self.assertEqual(b1, (0, len(self.block)))
        self.assertEqual(b2, (10, len(self.block)+10))

    def test_find_function_or_comment_not_prototype(self):
        p1 = find_function_or_comment(self.c)
        p2 = find_function_or_comment(self.c_and_f)
        p3 = find_function_or_comment(self.p_and_c)
        p4 = find_function_or_comment(self.p)
        self.assertEqual(len(p1), 0)
        self.assertEqual(len(p2), 1)
        self.assertEqual(len(p3), 0)
        self.assertEqual(len(p4), 0)

    def test_find_function_or_comment_multiple_matches(self):
        f = 'word /* comment */\nint func() {\nword}\n'
        f += 'word;\nvoid func(int a) {\nword;\n}'
        p1 = find_function_or_comment(f)
        self.assertEqual(len(p1), 2)

    def test_find_function_starts(self):
        p1 = find_function_start(self.c)
        p2 = find_function_start(self.c_and_f)
        p3 = find_function_start(self.p)
        p4 = find_function_start(self.p_and_f)
        self.assertEqual(p1, None)
        self.assertEqual(p2, (20, 44))
        self.assertEqual(p3, None)
        self.assertEqual(p4, (16, 35))

    def test_parse_functions_with_bodies(self):
        line = load_file('test_good_program.c')
        functions = [a for a in parse_functions_with_bodies(line)]
        self.assertEqual(len(functions), 3)
        self.assertNotEqual(functions[0].span()[0], 0)
        line2 = load_file('test_bad_program.c')
        functions2 = [a for a in parse_functions_with_bodies(line2)]
        self.assertEqual(len(functions2), 3)

    def test_parse_variable_declarations(self):
        vs = ['int i;', 'int i = 4;', 'int i, j = 6;',
             'int * j = &i;', 'char a = b + c / 8;',
             'unsigned int int * a;']
        ns = ['a + b;', 'a = m;', 'm = (int) m;', 'printf(\'%s\', x)']
        for v in vs:
            self.assertTrue(v in parse_variable_declarations(v))
        for n in ns:
            self.assertFalse(n in parse_variable_declarations(n))
        for v in vs:
            temp = parse_variable_declarations(
                choice(ns) + v + choice(ns)
                )
            self.assertTrue(v in temp)
            self.assertEqual(v, temp[0])

    def test_remove_given_ranges(self):
        l = 'a'*5 + 'b'*5 + 'c'*5 + 'd'*5
        no_b = [(5, 10),]
        no_a_b_d = [(0, 4), (5, 9), (15, 19)]
        no_a_b = [(0, 4), (3, 9)]
        self.assertTrue('b' not in remove_given_ranges(l, no_b))
        self.assertTrue('c' in remove_given_ranges(l, no_a_b_d))
        self.assertEqual(len(remove_given_ranges(l, no_a_b_d)), 5)
        self.assertTrue('a' not in remove_given_ranges(l, no_a_b))
        self.assertTrue('b' not in remove_given_ranges(l, no_a_b))
        self.assertEqual(len(remove_given_ranges(l, no_a_b)), 10)

    def test_replace_given_ranges(self):
        l = 'a'*5 + 'b'*5 + 'c'*5 + 'd'*5
        no_b = [(5, 10),]
        l2 = replace_given_ranges(l, no_b)
        self.assertEqual(len(l), len(l2))
        self.assertTrue(l2[5:10].isspace())
        self.assertTrue('b' not in l2)

    def test_parse_structs(self):
        structfile = load_file('test_structs.c')
        structs = parse_structs(structfile)
        self.assertEqual(len(structs), 4)
        self.assertTrue(structs[0].group().startswith('define'))
        self.assertTrue(structs[1].group().startswith('struct'))

    def test_parse_ifs(self):
        iffile = load_file('test_ifs.c')
        ifs = parse_ifs(iffile)
        self.assertEqual(len(ifs), 4)
        self.assertTrue('else if' in ifs[0].group())

    def test_parse_fors(self):
        pass


class TestDocumentationMethods(unittest.TestCase):


    def setUp(self):
        self.good_program = load_file('test_good_program.c')
        self.good_function = load_file('test_good_function.c')
        self.bad_program = load_file('test_bad_program.c')

    def test_file_contains_header(self):
        self.assertTrue(file_contains_header(self.good_program))
        self.assertFalse(file_contains_header(self.bad_program))

    def test_header_contains_necessary_fields(self):
        b1 = '/*\nName: John Doe\n*/'
        b2 = '/*\nName: John Doe\nSection: .....\nDue Date:\n*/'
        c1 = '/**\nName:\nSection:\nAssignment:\nDue Date:\nCredit:\n'
        c1 += 'Problem:\nSolution:\nErrors handled:\nLimitations:\n*/'
        rfield_n = len(REQUIRED_HEADER_SECTIONS)
        b1errors = header_contains_necessary_fields(b1)
        b2errors = header_contains_necessary_fields(b2)
        c1errors = header_contains_necessary_fields(c1)
        self.assertEqual(len(b1errors), rfield_n-1)
        self.assertEqual(len(b2errors), rfield_n-3)
        self.assertEqual(len(c1errors), rfield_n-9)

        program_h = get_file_header(self.good_program).group()
        self.assertEqual(len(header_contains_necessary_fields(program_h)), 0)

    def test_all_lines_eighty_characters(self):
        self.assertEqual(all_lines_eighty_characters(self.good_program), [])
        self.assertEqual(len(all_lines_eighty_characters(self.bad_program)), 1)
        self.assertEqual(len(all_lines_eighty_characters('a'*81 + '\n')), 1)

    def test_no_global_functions(self):
        self.assertTrue(no_global_functions(self.good_program) is None)
        self.assertEqual(len(no_global_functions(self.bad_program)), 3)


    def test_two_lines_before_functions(self):
        self.assertTrue(two_lines_before_functions(self.good_program) is None)
        self.assertEqual(len(two_lines_before_functions(self.bad_program)), 3)

    def test_indentation_level_three_spaces(self):
        self.assertTrue(indentation_level_three_spaces(self.good_program)
            is None)
        self.assertEqual(len(indentation_level_three_spaces(self.bad_program)),
            9)

    #### FUNCTION TESTS #######################################################

    def test_comment_before_function(self):
        good = comment_before_function(self.good_program)
        bad = comment_before_function(self.bad_program)
        self.assertEqual(len(good), 0)
        self.assertEqual(len(bad), 1)
        self.assertTrue('main' in bad[0])

    def test_no_comment_within_function(self):
        pass

    def test_prototypes_declared_for_all_uses(self):
        pass

    def test_function_not_too_long(self):
        pass

    def test_variable_declaration_alphabetical(self):
        pass

if __name__=='__main__':
    unittest.main()
