import datetime as dt
import itertools as it
import random
import sys
import typing as ty

import common as cmn
import data
import rdb
import rdb_batch as rb

def _binary_to_signal(iterator:  ty.Iterator[ty.Optional[bool]], inverse: bool=False) -> ty.Iterator[ty.Optional[float]]:
    to_signal = lambda b: 1 if b else 0
    if inverse:
        to_signal= lambda b: 0 if b else 1
    return map(lambda b: None if b is None else to_signal(b), iterator)

def dummy_values(max_v: float = None, min_v: float = None) -> ty.Iterator[float]:
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
def random_null(iterator: ty.Iterator[T]) -> ty.Iterator[T]:
    while True:
        yield next(iterator) if random.random() < 0.75 else None

Measurement = ty.Tuple[dt.datetime, int, float]
def dummy_measurements(sensors: ty.Dict[int, ty.Iterator[float]]) -> ty.Iterator[Measurement]:
    recs = rdb.execute_query("select max(measurement_time) as last_time from measurements")
    base_time = recs[0]['last_time']
    if base_time is None:
        base_time = dt.datetime.now() - dt.timedelta(hours=1)

    times: ty.Iterator[dt.datetime] = data.generate_times(base_time, min_seconds=0, max_seconds=3)
    for sensor_id, v in cmn.merged_sequences(sensors, max_reads=1000):
        time: dt.datetime = next(times)
        yield (time, sensor_id, v)

def insert_m2():
    target_table = 'm3'
    times = lambda base_time: data.generate_times(base_time, min_seconds=1, max_seconds=3)
    sql_cols = ['measurement_time'] + \
        [f'flag{i+1}' for i in range(10)] + \
        [f'data{i+1}' for i in range(20)]
    params_iters = \
        [dummy_active_states() for _ in range(5)] + \
        [dummy_fault_states() for _ in range(5)] + \
        [random_null(dummy_values(min_v=0, max_v=40)) for _ in range(5)] + \
        [random_null(dummy_values(min_v=50, max_v=100)) for _ in range(5)] + \
        [random_null(dummy_values(min_v=0, max_v=7)) for _ in range(2)] + \
        [random_null(dummy_values(min_v=0)) for _ in range(8)]
    _insert_recs(target_table, sql_cols, times, params_iters, 10000)

def insert_mer():
    times = lambda base_time: data.generate_times(base_time, min_seconds=1, max_seconds=3)
    sql_cols = ['unixtime'] + \
        [f'data{i+1:02d}' for i in range(56)]
    params_iters = \
        list(it.chain(*[[dummy_active_states(), dummy_fault_states()] for _ in range(7)])) + \
        [dummy_fault_states() for _ in range(2)] + \
        list(it.chain(*[[dummy_active_states(), dummy_fault_states()] for _ in range(9)])) + \
        [dummy_fault_states() for _ in range(2)] + \
        list(it.chain(*[[dummy_active_states(), dummy_fault_states()] for _ in range(9)])) + \
        [dummy_fault_states() for _ in range(2)]
    _insert_recs('_mer', sql_cols, times, params_iters, 100000)

def insert_mio():
    times = lambda base_time: data.generate_times(base_time, min_seconds=3, max_seconds=3)
    sql_cols = ['unixtime'] + \
        [f'data{i+33:02d}' for i in range(50)]
    params_iters = \
        [random_null(dummy_values(min_v=0, max_v=100)) for _ in range(50)]
        # [data.sine_wave(a=0, b=100, period=100 + (i % 5)) for i in range(50)]
    _insert_recs('_mio', sql_cols, times, params_iters, 100000)

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

def _insert_recs(
        target_table: str, 
        sql_cols: ty.List[str], 
        times: ty.Callable[[dt.datetime], ty.Iterator[dt.datetime]],
        params_iters: ty.List[ty.Iterator[ty.Any]], 
        steps: int) -> None:
    base_time = rdb.execute_query(f"select FROM_UNIXTIME(max({sql_cols[0]})) as last_time from {target_table}")[0]['last_time']
    if base_time is None:
        base_time = dt.datetime.now() - dt.timedelta(days=2)

    sql_params = ['%s' for _ in range(len(sql_cols))]
    sql = f"INSERT INTO {target_table}({', '.join(sql_cols)}) VALUES({', '.join(sql_params)})"

def insert(batches: list[rb.InsertBatch]) -> None:
    before, after = rb.split_and_flatten_batches(dt.datetime.now(), batches)
    inserter = lambda sql, params: rdb.insert_timed_values(sql, params, time_converter=lambda x: x.timestamp())
    rdb.insert_timed_values(sql, it.islice(zip(times(base_time), *params_iters), steps), time_converter=lambda x: x.timestamp())

def insert_measurements(recs: ty.Iterator[Measurement]) -> None:
    recs = filter(lambda rec: rec[2] is not None, recs)
    sql = """
        INSERT INTO measurements (measurement_time, sensor_assignment_id, measured_value)
        VALUES (%s, %s, %s);
        """
    rdb.insert_timed_values(sql, recs)

def insert_dummy_measurements() -> None:
    """
    | 1000 | tankA_temperature_inlet  |
    | 1001 | tankA_temperature_outlet |
    | 1010 | tankA_pH                 |
    | 2000 | heatpump1_temperature    |
    | 2100 | heatpump1_active         |
    | 2110 | heatpump1_fault          |
    | 3000 | heatpump2_temperature    |
    | 3100 | heatpump2_active         |
    | 3110 | heatpump2_fault          |
    | 4100 | blower1_active           |
    """
    sensors: ty.Dict[int, ty.Iterator[float]] = {
        1000: dummy_values(), 
        1001: dummy_values(), 
        1010: dummy_values(), 
        2000: dummy_values(), 
        2100: dummy_active_states(), 
        2110: dummy_fault_states(),  
        3000: dummy_values(), 
        3100: dummy_active_states(), 
        3110: dummy_fault_states(),  
        4100: dummy_active_states(), 
    }
    insert_measurements(dummy_measurements(sensors))

if __name__ == "__main__":
    # insert_dummy_measurements()
    # insert_m2()
    if len(sys.argv) > 1:
        insert_mer()
    else:
        insert_mio()
    # insert_mer2()
