import logging
from unicodedata import name
import simple_orm
from simple_orm import resource
from simple_orm.table import SimpleTable


class Demo(SimpleTable):
    TABLE_NAME = 'demo_table'


def setup_logger():
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    logger = logging.getLogger('simple_orm')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(sh)


def setup_connections():
    config = {
        'default': [
            {
                'host': '127.0.0.1',
                'port': 3306,
                'password': 'password',
                'user': 'root',
                'database': 'test',
            },
        ],
    }
    simple_orm.setup_connections(config)


def create_demo_table():
    conn = resource.manager['default']
    conn.raw_exec('drop table if exists demo_table')
    table_schema = '''create table demo_table (
        id int primary key AUTO_INCREMENT,
        name text,
        email text
    ) Engine=InnoDB'''
    conn.raw_exec(table_schema)


def main():
    setup_logger()
    setup_connections()
    create_demo_table()
    assert Demo.count(id=1) == 0
    record_1 = {'name': 1, 'email': "1@1.com"}
    record_2 = {'name': 2, 'email': "2@2.com"}
    record_3 = {'name': 3, 'email': "3@3.com"}
    Demo.insert(**record_1)
    assert Demo.count(name=1) == 1
    assert Demo.first(name=1)['email'] == '1@1.com'
    Demo.batch_insert([record_2, record_3])
    assert Demo.count(name=2) == 1
    assert Demo.count(name=3) == 1
    assert Demo.first(name=2)['email'] == '2@2.com'
    assert Demo.query(name=3)[0]['email'] == '3@3.com'
    # test customize cols
    name_list = []
    for item in Demo.range_by_pk(0, 100, batch_size=2, cols=['id', 'name']):
        name_list.append(item['name'])
    assert name_list == ['1', '2', '3']
    # test all cols
    name_list = []
    for item in Demo.range_by_pk(0, 100, batch_size=2):
        name_list.append(item['name'])
    assert name_list == ['1', '2', '3']
    # test query
    assert Demo.count(name__in=['1', '3']) == 2
    assert Demo.count(id__gt=1) == 2
    assert Demo.count(id__gte=1) == 3
    assert Demo.count(id__lt=2) == 1
    assert Demo.count(id__lte=2) == 2
    assert Demo.count(id__lte=2, name__in=['1', '2']) == 2

    simple_orm.close_connections()


if __name__ == '__main__':
    main()