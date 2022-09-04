import re

pattern_table_name = re.compile(r'^[a-zA-Z0-9_]+$')


class DotDict(dict):
    """access key via dot method
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f'{type(self)} has no field {key}')

    def __setattr__(self, key, value):
        self[key] = value


def assert_valid_table_name(table_name):
    """ check table name is valid
    """
    assert pattern_table_name.match(table_name), \
        f'invalid table_name {table_name}'


def parse_conditions(conditions):
    """ convert id__in=[1,2,3] to `id` in %s
    """
    if not conditions:
        raise ValueError(f'empty conditions')
    cols, args = zip(*conditions.items())
    cols_sql_lst = []
    for col in cols:
        operator = ''
        if '__' in col:
            col, operator = col.split('__', 1)
        if operator == 'gt':
            cols_sql_lst.append(f'`{col}` > %s')
        elif operator == 'gte':
            cols_sql_lst.append(f'`{col}` >= %s')
        elif operator == 'lt':
            cols_sql_lst.append(f'`{col}` < %s')
        elif operator == 'lte':
            cols_sql_lst.append(f'`{col}` <= %s')
        elif operator == 'in':
            cols_sql_lst.append(f'`{col}` in %s')
        else:
            cols_sql_lst.append(f'`{col}` = %s')
    return ' AND '.join(cols_sql_lst), args
