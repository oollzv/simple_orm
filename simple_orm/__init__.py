from simple_orm import resource
from simple_orm.connection import ConnectionManager


def setup_connections(config):
    manager = ConnectionManager()
    for conn_name, conn_arg_list in config.items():
        for conn_arg in conn_arg_list:
            manager.add_connection(conn_name, conn_arg)
    resource.manager = manager
    return manager


def close_connections():
    resource.manager.close_connections()