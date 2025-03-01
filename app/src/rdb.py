import datetime as dt
import itertools as it
import time as ti
import typing as ty

import pymysql
import util as u

# データベース接続情報
DB_HOST = 'mariadb'  # MariaDBのホスト名
DB_USER = 'user'       # ユーザー名
DB_PASSWORD = 'rdbpass'  # パスワード
DB_NAME = 's1'  # データベース名


T=ty.TypeVar('T')
def execute(callback: ty.Callable[[pymysql.connections.Connection], T]) -> T:
    """
    Executes a database operation within a managed connection.

    :param callback: A callable that takes a pymysql connection object and returns a result.
    :type callback: Callable[[pymysql.connections.Connection], T]
    :return: The result of the callback function.
    :rtype: T

    The function establishes a connection to the database using the internal credentials and 
    passes the connection object to the callback function. The connection is automatically 
    closed after the callback function is executed.
    """
    with pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    ) as connection:
        return callback(connection)

def execute_query(query: str):
    def _f(connection):
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    return execute(_f)

def execute_update(
        update_query: str,
        params_iter: ty.Iterator[tuple], 
        time_converter: ty.Callable[[dt.datetime], ty.Any] = lambda x: x,
        commit_interval: int = 2000) -> None:
    """
    Executes an update query in batches with a specified commit interval.
    Args:
        update_query (str): The SQL update query to be executed.
        params_iter (Iterator[Tuple]): An iterator of tuples containing the parameters for the update query.
        commit_interval (int, optional): The number of update operations to execute before committing the transaction. Defaults to 2000.
    Returns:
        None
    """
    def _f(connection):
        with connection.cursor() as cursor:
            for params_set in u.chunked(params_iter, commit_interval):
                n = 0
                for params in params_set:
                    _params = [time_converter(params[0]), *params[1:]]
                    cursor.execute(update_query, _params)
                    n += cursor.rowcount
                assert n > 0, 'No records were updated.'
                connection.commit()
                print(f'{dt.datetime.now()}: {n} of records was inserted.')

    execute(_f)
