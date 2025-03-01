import datetime as dt
import itertools as it
import random
import sys
import typing as ty

import util as u
import data
import rdb
import rdb_batch as rb

def _binary_to_signal(iterator:  ty.Iterator[ty.Optional[bool]], inverse: bool=False) -> ty.Iterator[ty.Optional[float]]:
    to_signal = lambda b: 1 if b else 0
    if inverse:
        to_signal= lambda b: 0 if b else 1
    return map(lambda b: None if b is None else to_signal(b), iterator)

def dummy_values(max_v: float, min_v: float) -> ty.Iterator[float]:
    delta = 5
    choices = [v/10 for v in range(-delta * 10, delta * 10 + 1)]
    state = data.State(current=0, choices=choices)
    # return data.generate_dynamic_sequence(state, max_v, min_v)
    return data.bounded_random_wave(min_v, max_v, step_size=0.2, central_ratio=0.8)

def _dummy_flags() -> ty.Iterator[ty.Optional[bool]]:
    return data.unique_values(
        data.generate_binary_states(prob_false_to_true=0.5, prob_true_to_false=0.9, initial_state=True),
    )

dummy_active_states = lambda: _binary_to_signal(_dummy_flags())
dummy_fault_states = lambda: _binary_to_signal(_dummy_flags(), inverse=True)

T=ty.TypeVar('T')
def random_null(iterator: ty.Iterator[T]) -> ty.Iterator[ty.Optional[T]]:
    while True:
        yield next(iterator) if random.random() < 0.75 else None


def create_mer_recs() -> rb.InsertBatch:
    gen_times = lambda base_time: data.generate_times(base_time, min_seconds=1, max_seconds=3)
    sql_cols = ['unixtime'] + \
        [f'data{i+1:02d}' for i in range(56)]
    params_iters = \
        list(it.chain(*[[dummy_active_states(), dummy_fault_states()] for _ in range(7)])) + \
        [dummy_fault_states() for _ in range(2)] + \
        list(it.chain(*[[dummy_active_states(), dummy_fault_states()] for _ in range(9)])) + \
        [dummy_fault_states() for _ in range(2)] + \
        list(it.chain(*[[dummy_active_states(), dummy_fault_states()] for _ in range(9)])) + \
        [dummy_fault_states() for _ in range(2)]
    return _create_recs('_mer', sql_cols, gen_times, params_iters)

def create_mio_recs() -> rb.InsertBatch:
    gen_times = lambda base_time: data.generate_times(base_time, min_seconds=3, max_seconds=3)
    sql_cols = ['unixtime'] + \
        [f'data{i+33:02d}' for i in range(50)]
    params_iters = \
        [random_null(dummy_values(min_v=0, max_v=100)) for _ in range(50)]
        # [data.sine_wave(a=0, b=100, period=100 + (i % 5)) for i in range(50)]
    return _create_recs('_mio', sql_cols, gen_times, params_iters)

def insert_mer2():
    now = dt.datetime.now()
    firing_time = now + dt.timedelta(seconds=5)
    resolved_time = firing_time + dt.timedelta(seconds=45)
    rdb.insert_timed_values("""
        INSERT INTO _mer(unixtime, data13) VALUES(%s, %s)
        """,
        [
            [now, 1],
            [firing_time, 0],
            [resolved_time, 1]
        ], time_converter=lambda x: x.timestamp())

def _create_recs(
        target_table: str, 
        sql_cols: list[str], 
        gen_times: ty.Callable[[dt.datetime], ty.Iterator[dt.datetime]],
        params_iters: list[ty.Iterator[ty.Any]]
        ) -> rb.InsertBatch:
    base_time = rdb.execute_query(f"select FROM_UNIXTIME(max({sql_cols[0]})) as last_time from {target_table}")[0]['last_time']
    if base_time is None:
        base_time = dt.datetime.now() - dt.timedelta(days=2)
    times = gen_times(base_time)

    sql_params = ['%s' for _ in range(len(sql_cols))]
    sql = f"INSERT INTO {target_table}({', '.join(sql_cols)}) VALUES({', '.join(sql_params)})"
    return rb.create_insert_batch(sql, times, params_iters)

def insert(batches: list[rb.InsertBatch], steps_after: int) -> None:
    inserter = lambda sql, params: rdb.execute_update(sql, params, time_converter=lambda x: x.timestamp())
    before, after = rb.split_and_flatten_batches(dt.datetime.now(), batches)
    for batch in before:
        rb.apply(inserter, batch)
    rb.apply_with_delay(inserter, after, steps_after)


if __name__ == "__main__":
    # insert_dummy_measurements()
    # insert_m2()
    insert([create_mer_recs(), create_mio_recs()], 1000)
    # insert_mer2()
