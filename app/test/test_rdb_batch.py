import datetime as dt
import rdb_batch as rb

def _sec(seconds: int) -> dt.datetime:
    return dt.datetime(2021, 9, 1, 0, 0, seconds)

def test_create_insert_batch():
    sql = "INSERT INTO _mer(unixtime, data13) VALUES(%s, %s)"
    times = iter([_sec(0), _sec(1), _sec(2)])
    params_iters = [
        iter([1, 2, 3]),
        iter([4, 5, 6])
        ]
    batch = rb.create_insert_batch(sql, times, params_iters)
    assert batch.sql == sql
    assert list(batch.params_iter) == [
        rb.InsertParams(_sec(0), [1, 4]),
        rb.InsertParams(_sec(1), [2, 5]),
        rb.InsertParams(_sec(2), [3, 6])
    ]

def test_split_insert_batch():
    split_sec = _sec(1)
    batch = rb.InsertBatch(
        "INSERT INTO _mer(unixtime, data13) VALUES(%s, %s)",
        iter([
            rb.InsertParams(_sec(0), [1, 4]),
            rb.InsertParams(_sec(1), [2, 5]),
            rb.InsertParams(_sec(2), [3, 6])
        ])
    )
    before, after = rb.split_insert_batch(split_sec, batch)
    assert before.sql == batch.sql
    assert list(before.params_iter) == [
        rb.InsertParams(_sec(0), [1, 4])
        ]
    assert after.sql == batch.sql
    assert list(after.params_iter) == [
        rb.InsertParams(_sec(1), [2, 5]), 
        rb.InsertParams(_sec(2), [3, 6])
        ]
