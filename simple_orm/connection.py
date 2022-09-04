from collections import defaultdict
import logging
import time
import random

import pymysql

from . import utils

logger = logging.getLogger("simple_orm")


class ConnectionManager:

    def __init__(self):
        self.connections = defaultdict(list)

    def add_connection(self, name, conn_arg):
        connection = Connection.new_conn(name, **conn_arg)
        self.connections[name].append(connection)

    def __getitem__(self, name):
        connections = self.connections.get(name)
        if connections:
            return random.choice(connections)
        return None

    def close_connections(self):
        for _, connections in self.connections.items():
            for connection in connections:
                connection.close()


class Connection:
    """mysql connection object
    """

    def __init__(self, name, lazy_connect):
        self._lazy_connect = lazy_connect
        self._raw_conn = None
        self._conn_name = name

    @property
    def raw_conn(self):
        if not self._raw_conn:
            self._raw_conn = self._lazy_connect()
            logger.debug('connection %s connected\t%s', self._conn_name,
                         self.conn_host)
        return self._raw_conn

    def close(self):
        """close database connection
        """
        if self._raw_conn:
            self._raw_conn.close()
            self._raw_conn = None
            logger.debug('connection %s closed', self._conn_name)

    def raw_exec(self, sql, args=None):
        """execute sql with args
        """
        last_insert_id = None
        rows_affected = None
        start_at = time.time()
        try:
            with self.raw_conn.cursor() as cursor:
                cursor.execute(sql, args=args)
                rows_affected = cursor.rowcount
                last_insert_id = cursor.lastrowid
            self.raw_conn.commit()
        finally:
            time_cost = time.time() - start_at
            logger.debug(
                'conn: %stime_cost:%s\tsql: %s\targs:%s\tlast_insert_id:%s\trows_affected:%s',
                self.conn_host, time_cost, sql, args, last_insert_id,
                rows_affected)
        return last_insert_id, rows_affected

    def raw_query(self, sql, args=None, size=1000):
        """execute 
        """
        start_at = time.time()
        res = []
        try:
            with self.raw_conn.cursor() as cursor:
                cursor.execute(sql, args=args)
                res = cursor.fetchmany(size)
        finally:
            time_cost = time.time() - start_at
            logger.debug(
                'conn: %s\ttime_cost:%s\tsql: %s\targs: %s res_length: %s',
                self.conn_host, time_cost, sql, args, len(res))
        return [utils.DotDict(**item) for item in res]

    def raw_query_one(self, sql, args=None):
        start_at = time.time()
        res = None
        try:
            with self.raw_conn.cursor() as cursor:
                cursor.execute(sql, args=args)
                res = cursor.fetchone()
        finally:
            time_cost = time.time() - start_at
            logger.debug('conn: %s\ttime_cost:%s\tsql: %s\targs: %s res: %s',
                         self.conn_host, time_cost, sql, args, res)
        res = res and utils.DotDict(**res)
        return res

    def count(self, table_name, **conditions):
        """get record count which match conditions
        """
        utils.assert_valid_table_name(table_name)
        if not conditions:
            raise ValueError(f'empty conditions')
        col_sql, args = utils.parse_conditions(conditions)
        sql = f'select count(1) as total from `{table_name}` where {col_sql}'
        return self.raw_query_one(sql, args)['total']

    def query(self, table_name, _size=1000, **conditions):
        """return _size result which match conditions
        """
        utils.assert_valid_table_name(table_name)
        col_sql, args = utils.parse_conditions(conditions)
        sql = f'select * from `{table_name}` where {col_sql}'
        return self.raw_query(sql, args, size=_size)

    def first(self, table_name, **conditions):
        """return the first result which match condition
        """
        utils.assert_valid_table_name(table_name)
        col_sql, args = utils.parse_conditions(conditions)
        sql = f'select * from `{table_name}` where {col_sql}'
        return self.raw_query_one(sql, args)

    def insert(self, table_name, **row):
        """insert record to table_name 
        """
        utils.assert_valid_table_name(table_name)
        cols, args = zip(*row.items())
        cols_sql = ','.join(f'`{col}`' for col in cols)
        values_sql = ','.join('%s' for _ in cols)
        sql = f'insert into `{table_name}`({cols_sql}) values ({values_sql})'
        return self.raw_exec(sql, args)

    def batch_insert(self, table_name, rows):
        """insert many records to table
        """
        utils.assert_valid_table_name(table_name)
        cols = sorted(rows[0].keys())
        args = []
        cols_sql = ','.join(f'`{col}`' for col in cols)
        values_sql_lst = []
        for row in rows:
            values_placeholder = ','.join('%s' for _ in cols)
            values_sql_lst.append(f'({values_placeholder})')
            args.extend(row[col] for col in cols)
        values_sql = ','.join(values_sql_lst)
        sql = f'insert into `{table_name}`({cols_sql}) values {values_sql}'
        return self.raw_exec(sql, args)

    @property
    def conn_host(self):
        return f'{self.raw_conn.host}:{self.raw_conn.port}'

    @classmethod
    def new_conn(cls, name, **conn_args):
        defaults = {
            'use_unicode': True,
            'charset': 'utf8',
            'autocommit': False,
            'cursorclass': pymysql.cursors.DictCursor,
        }
        for key, value in conn_args.items():
            if key in defaults:
                defaultdict[key] = value
        defaults.update
        connect = lambda: pymysql.connect(
            host=conn_args['host'],
            port=conn_args['port'],
            user=conn_args['user'],
            password=conn_args['password'],
            database=conn_args['database'],
            **defaults,
        )
        return cls(name, connect)
