import datetime as dt
import rdb_batch as rb

def test_create_insert_batch():
    sql = "INSERT INTO _mer(unixtime, data13) VALUES(%s, %s)"
    times = iter([
        dt.datetime(2021, 9, 1, 0, 0, 0), 
        dt.datetime(2021, 9, 1, 0, 0, 1), 
        dt.datetime(2021, 9, 1, 0, 0, 2)
        ])
    params_iters = [iter([1, 2, 3]), iter([4, 5, 6])]
    batch = rb.create_insert_batch(sql, times, params_iters)
    assert batch.sql == sql
    assert list(batch.params_iter) == [
        rb.InsertParams(dt.datetime(2021, 9, 1, 0, 0, 0), [1, 4]),
        rb.InsertParams(dt.datetime(2021, 9, 1, 0, 0, 1), [2, 5]),
        rb.InsertParams(dt.datetime(2021, 9, 1, 0, 0, 2), [3, 6])
    ]
