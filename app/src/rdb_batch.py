import datetime as dt
import dataclasses as dc
import itertools as it
import time as ti
import typing as ty

import date_util as du

@dc.dataclass
class InsertParams:
    time: dt.datetime
    values: list[float]

    def to_tuple(self) -> tuple:
        return (self.time, *self.values)

@dc.dataclass
class InsertBatch:
    sql: str
    params_iter: ty.Iterator[InsertParams]

@dc.dataclass
class InsertTask:
    sql: str
    params: InsertParams


def apply(inserter: ty.Callable[[str, ty.Iterator[tuple]], ty.Any], insert_batch: InsertBatch) -> None:
    inserter(insert_batch.sql, ((p.time, *p.values) for p in insert_batch.params_iter))

def apply_with_delay(
        inserter: ty.Callable[[str, ty.Iterator[tuple]], ty.Any],
        insert_tasks: ty.Iterator[InsertTask],
        steps: int
        ) -> None:
    for _ in range(steps):
        insert_task = next(insert_tasks, None)
        if insert_task is None:
            break
        params: InsertParams = insert_task.params
        du.execute_at(params.time, lambda: inserter(insert_task.sql, iter([params.to_tuple()])))


def split_insert_batch(split_time: dt.datetime, insert_batch: InsertBatch) -> tuple[InsertBatch, InsertBatch]:
    """
    InsertBatchを指定された時刻を基準に前半と後半に分割する。

    :param split_time: 分割基準となる日時
    :param insert_batch: 分割対象のInsertBatch
    :return: (前半のInsertBatch, 後半のInsertBatch)
    """
    iter1, iter2 = it.tee(insert_batch.params_iter, 2)
    before_params = (p for p in iter1 if p.time < split_time)
    after_params = (p for p in iter2 if p.time >= split_time)

    return (
        InsertBatch(insert_batch.sql, before_params),
        InsertBatch(insert_batch.sql, after_params)
    )

def flatten_insert_batches(batches: list[InsertBatch]) -> ty.Iterator[InsertTask]:
    """
    InsertBatchのリストを受け取り、各SQLとパラメータを組み合わせて順次生成するジェネレータ。

    :param batches: InsertBatchのリスト
    :return: Iterator[InsertTask]

    例:
    ```
    batches = [
        InsertBatch("sql1", iter([
            InsertParams(t1, [1]),
            InsertParams(t2, [2]),
            InsertParams(t3, [3]),
            InsertParams(t4, [4]),
            ])),
        InsertBatch("sql2", iter([
            InsertParams(t5, [5]),
            InsertParams(t6, [6])
            ]))
    ]
    flatten_insert_batches(batches) -> [
        InsertTask("sql1", InsertParams(t1, [1])),
        InsertTask("sql2", InsertParams(t6, [6])),
        InsertTask("sql1", InsertParams(t2, [2])),
        InsertTask("sql2", InsertParams(t5, [5])),
        InsertTask("sql1", InsertParams(t3, [3])),
        InsertTask("sql1", InsertParams(t4, [4]))
    ]
    """
    insert_tasks_list: list[ty.Iterator[InsertTask]] = [_to_task(batch) for batch in batches]
    for insert_tasks in it.zip_longest(*insert_tasks_list):
        for insert_task in insert_tasks:
            if insert_task is not None:
                yield insert_task

def _to_task(batch: InsertBatch) -> ty.Iterator[InsertTask]:
    for p in batch.params_iter:
        yield InsertTask(batch.sql, p)

def split_and_flatten_batches(
        split_time: dt.datetime, batches: list[InsertBatch]
    ) -> tuple[list[InsertBatch], ty.Iterator[InsertTask]]:
    """
    各InsertBatchをsplit_timeで分割し、前半と後半に分ける。

    :param split_time: 分割基準となる日時
    :param batches: 分割対象のInsertBatchリスト
    :return: (前半部のInsertBatchリスト, 後半部をflattenしたInsertTaskのイテレータ)
    """
    before_batches = []
    after_batches = []

    # 各バッチをsplit_timeで分割
    for batch in batches:
        before, after = split_insert_batch(split_time, batch)
        if before.params_iter:
            before_batches.append(before)
        if after.params_iter:
            after_batches.append(after)

    # 後半部をflatten
    flattened_after_tasks = flatten_insert_batches(after_batches)

    return before_batches, flattened_after_tasks

def create_insert_batch(
        sql: str, 
        times: ty.Iterator[dt.datetime],
        params_iters: list[ty.Iterator[ty.Any]]
        ) -> InsertBatch:
    """
    指定された条件でInsertBatchを生成する。
    
    :param sql: SQL文
    :param times: 時刻のイテレータ
    :param params_iters: パラメータのイテレータのリスト
    :return: InsertBatch
    """
    return InsertBatch(sql, create_insert_params(times, params_iters))

def create_insert_params(
        times: ty.Iterator[dt.datetime],
        params_iters: list[ty.Iterator[ty.Any]]
        ) -> ty.Iterator[InsertParams]:
    """
    指定された条件でInsertParamsを生成するジェネレータを生成する。
    
    :param times: 時刻のイテレータ
    :param params_iters: パラメータのイテレータのリスト
    :return: InsertParamsのイテレータ

    例:
    ```
    times = [t1, t2, t3, t4]
    params_iters = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
    create_insert_params(times, params_iters) -> [
        InsertParams(t1, 1, 5, 9),
        InsertParams(t2, 2, 6, 10),
        InsertParams(t3, 3, 7, 11),
        InsertParams(t4, 4, 8, 12)
    ]
    ```
    """
    for time, *params in it.zip_longest(times, *params_iters):
        yield InsertParams(time, params)
        