import datetime as dt
import dataclasses as dc
import itertools as it
import time as ti
import typing as ty

import date_util as du

@dc.dataclass
class InsertParams:
    time: datetime
    values: list[float]

@dc.dataclass
class InsertBatch:
    sql: str
    params_iter: ty.Iterator[InsertParams]

@dc.dataclass
class InsertTask:
    sql: str
    params: InsertParams


def apply(inserter: ty.Callable[[str, ty.Iterator[tuple]], ty.Any], insert_batch: InsertBatch) -> None:
    inserter(self.sql, ((p.time, *p.values) for p in insert_batch.params_iter))

def apply_with_delay(
        inserter: ty.Callable[[str, ty.Iterator[tuple]], ty.Any],
        insert_tasks: ty.Iterator[InsertTask]
        ) -> None:
    for insert_task in insert_tasks:
        du.execute_at(insert_task.time, lambda: inserter(insert_task.sql, [(insert_task.time, *insert_task.values)]))


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
    """
    # 各バッチのパラメータイテレータを取得
    param_iters = [batch.params_iter for batch in batches]

    # パラメータを順次取得し、それに対応するSQLと組み合わせて生成
    for params in it.zip_longest(*param_iters):
        for batch, param in zip(batches, params):
            if param is not None:
                yield InsertTask(batch.sql, param)


def split_and_flatten_batches(
        split_time: datetime, batches: list[InsertBatch]
    ) -> tuple[list[InsertBatch], Iterator[InsertTask]]:
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
