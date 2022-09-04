from simple_orm import resource


class SimpleTable:
    DB_NAME = 'default'
    TABLE_NAME = 'table'
    PK = 'id'

    @classmethod
    def get_conn(cls):
        manager = resource.manager
        return manager[cls.DB_NAME]

    @classmethod
    def count(cls, **conditions):
        conn = cls.get_conn()
        return conn.count(cls.TABLE_NAME, **conditions)

    @classmethod
    def first(cls, **conditions):
        conn = cls.get_conn()
        return conn.first(cls.TABLE_NAME, **conditions)

    @classmethod
    def query(cls, _size=1000, **conditions):
        conn = cls.get_conn()
        return conn.query(cls.TABLE_NAME, _size=_size, **conditions)

    @classmethod
    def insert(cls, **row):
        conn = cls.get_conn()
        return conn.insert(cls.TABLE_NAME, **row)

    @classmethod
    def batch_insert(cls, rows):
        conn = cls.get_conn()
        return conn.batch_insert(cls.TABLE_NAME, rows)

    @classmethod
    def range_by_pk(cls, min_id, max_id, *, batch_size=1000, cols=None):
        """return records which pk < min_id and pk > max_id
        """
        assert min_id < max_id
        cols_sql = '*'
        if cols and len(cols) > 0:
            cols_sql = ','.join(f'`{col}`' for col in cols)
        sql = f'SELECT {cols_sql} FROM `{cls.TABLE_NAME}` WHERE '\
            f'{cls.PK} > %s order by {cls.PK} limit %s'
        current_id = min_id - 1
        while current_id < max_id:
            args = [current_id, batch_size]
            conn = cls.get_conn()
            lst = conn.raw_query(sql, args, size=batch_size)
            if not lst:
                break
            current_id = lst[-1][cls.PK]
            for item in lst:
                if item[cls.PK] <= max_id:
                    yield item