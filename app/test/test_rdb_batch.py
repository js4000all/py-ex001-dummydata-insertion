import datetime as dt
import typing as ty

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

def test_flatten_insert_batches():
    sql1 = "sql1"
    sql2 = "sql2"
    batches = [
        rb.InsertBatch(
            sql1, 
            iter([
                rb.InsertParams(_sec(0), [1]),
                rb.InsertParams(_sec(3), [2]),
                rb.InsertParams(_sec(6), [3]),
                rb.InsertParams(_sec(9), [4])
            ])
        ),
        rb.InsertBatch(
            sql2, 
            iter([
                rb.InsertParams(_sec(1), [11]),
                rb.InsertParams(_sec(2), [12])
            ])
        )
    ]
    flattened: ty.Iterator[InsertTask] = rb.flatten_insert_batches(batches)
    assert list(flattened) == [
        rb.InsertTask(sql1, rb.InsertParams(_sec(0), [1])),
        rb.InsertTask(sql2, rb.InsertParams(_sec(1), [11])),
        rb.InsertTask(sql1, rb.InsertParams(_sec(3), [2])),
        rb.InsertTask(sql2, rb.InsertParams(_sec(2), [12])),
        rb.InsertTask(sql1, rb.InsertParams(_sec(6), [3])),
        rb.InsertTask(sql1, rb.InsertParams(_sec(9), [4]))
    ]
