import unittest

from simple_orm.utils import DotDict, assert_valid_table_name, parse_conditions


class TestTableName(unittest.TestCase):

    def test_valid_table(self):
        valid_table_names = ['hello']
        for table_name in valid_table_names:
            assert_valid_table_name(table_name)

        invalid_table_names = ['asd asd', 'select * ', '`asd`']
        for table_name in invalid_table_names:
            with self.assertRaises(AssertionError):
                assert_valid_table_name(table_name)


class TestParseConditions(unittest.TestCase):

    def test_parse_conditions(self):
        conditions = {
            'a': 1,
            'b__gt': 2,
            'c__gte': 3,
            'd__lt': 4,
            'd__lte': 5,
            'e__in': 6,
        }
        got_sql, got_args = parse_conditions(conditions)
        want_sql = '`a` = %s AND `b` > %s AND `c` >= %s AND `d` < %s AND `d` <= %s AND `e` in %s'
        want_args = (1, 2, 3, 4, 5, 6)
        self.assertEqual(want_sql, got_sql)
        self.assertEqual(want_args, got_args)


class TestDotDict(unittest.TestCase):

    def test_getattr(self):
        dot = DotDict(foo='bar')
        self.assertEqual(dot.foo, 'bar')
        with self.assertRaises(AttributeError):
            dot.key_not_exist

        dot.foo = 'barbar'
        self.assertEqual(dot.foo, 'barbar')
        self.assertEqual(dot.foo, dot['foo'])