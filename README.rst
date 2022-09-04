# simple_orm

## Description

```python
# connection manager
simple_orm.setup_connections(config)
conn = resource.manager['default']
# raw sql execute
conn.raw_exec('drop table if exists demo_table')
```

more example see [demo.py](demo.py)
