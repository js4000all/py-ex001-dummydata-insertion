import dataclasses as dc
import datetime as dt
import itertools as it
import math
import random
import time
import typing as ty

T=ty.TypeVar('T')

@dc.dataclass
class State:
    current: float
    choices: ty.Sequence[float]

Weights = ty.Sequence[float]
ChoicedState = float

WeightFunc = ty.Callable[[State], Weights]
UpdateStateFunc = ty.Callable[[State, ChoicedState], State]
ChoiceFunc = ty.Callable[[State, Weights], ChoicedState]

calc_proximity_weights: WeightFunc = lambda state: [1 / (1 + abs(state.current - choice)) for choice in state.choices]
update_state: UpdateStateFunc = lambda state, choiced_state: dc.replace(state, current=state.current-0.5 if choiced_state > 0 else state.current+0.5) 
choice_func: ChoiceFunc = lambda state, weights: random.choices(state.choices, weights=weights, k=1)[0]

def generate_dynamic_sequence(
        initial_state: State,
        max_v: ty.Optional[float] = None, 
        min_v: ty.Optional[float] = None,
        weight_func: WeightFunc = calc_proximity_weights, 
        update_state_func: UpdateStateFunc = update_state, 
        random_func: ChoiceFunc = choice_func) -> ty.Iterator[float]:
    state = initial_state
    last_value: float = 0  # 最後の返却値

    while True:
        weights = weight_func(state)
        chosen_delta: ChoicedState = random_func(state, weights)
        last_value += chosen_delta
        if max_v is not None and max_v < last_value:
            last_value = max_v
        if min_v is not None and min_v > last_value:
            last_value = min_v
        #print(f'{last_value} <- delta={chosen_delta} base={base_value} weights=[{weights_to_percentage_string(weights)}]')
        yield last_value
        state = update_state_func(state, chosen_delta)

def generate_binary_states(
        prob_false_to_true: float, prob_true_to_false: float,
        initial_state: bool = False,
        random_func: ty.Callable[[], float] = random.random) -> ty.Iterator[bool]:
    """
    二値状態を生成するジェネレータ。

    :param steps: 生成するステップ数
    :param prob_false_to_true: False から True への遷移確率
    :param prob_true_to_false: True から False への遷移確率
    :param initial_state: 初期状態 (デフォルトは False)
    :param random_func: 乱数生成関数 (デフォルトは random.random)
    :return: 二値状態のイテレータ
    """
    state: bool = initial_state  # 初期状態

    while True:
        yield state
        if state:
            if random_func() < prob_true_to_false:
                state = not state
        else:
            if random_func() < prob_false_to_true:
                state = not state

def bounded_random_wave(a: float, b: float, step_size: float = 0.1, central_ratio: float = 0.6) -> ty.Iterator[float]:
    """
    中央範囲ではランダムな変動、上下の範囲では中央に戻る力を強めた波形を生成する無限ジェネレータ。

    :param a: 最小値
    :param b: 最大値
    :param step_size: 1ステップあたりの最大変動量
    :param central_ratio: 中央範囲の比率（0.0 から 1.0）
    :return: floatのジェネレータ
    """
    mid = (a + b) / 2
    range_central = (b - a) * (central_ratio / 2)
    lower_threshold = mid - range_central
    upper_threshold = mid + range_central

    value = mid

    while True:
        if value < lower_threshold:
            # 下位領域では上昇しやすい
            bias = random.uniform(0, step_size)
        elif value > upper_threshold:
            # 上位領域では下降しやすい
            bias = random.uniform(-step_size, 0)
        else:
            # 中央範囲ではランダム
            bias = random.uniform(-step_size, step_size)

        value += bias
        value = max(a, min(b, value))  # 範囲外に出ないように制限

        yield value

def sine_wave(a: float, b: float, period: int) -> ty.Iterator[float]:
    """
    所定の周期と振幅で正弦波を生成する無限ジェネレータ。

    :param a: 最小値
    :param b: 最大値
    :param period: 周期（ステップ数で表す）
    :return: floatのジェネレータ
    """
    amplitude = (b - a) / 2
    mid = (a + b) / 2

    for step in it.cycle(range(period)):
        value = mid + amplitude * math.sin(2 * math.pi * step / period)
        yield value


def repeat_elements(iterator: ty.Iterator[T], n: int) -> ty.Iterator[T]:
    """
    Repeats each element in the given iterator a specified number of times.

    :param iterator: An iterator that yields elements of type T.
    :param n: The number of times to repeat each element.
    :return: An iterator that yields each element from the input iterator repeated n times.
    """
    return it.chain.from_iterable(it.repeat(x, n) for x in iterator)


def lock_state(generator: ty.Iterator[bool], lock_count: int) -> ty.Iterator[bool]:
    """
    Wraps a boolean generator to enforce a lock state for a specified number of iterations.

    Args:
        generator (Iterator[bool]): An iterator that yields boolean values.
        lock_count (int): The number of iterations to maintain the lock state after encountering a True value.

    Yields:
        Iterator[bool]: An iterator that yields boolean values, where True values are followed by a locked state for the specified number of iterations.
    """
    # Function implementation here
    lock_remaining = 0

    for state in generator:
        if lock_remaining > 0:
            yield True
            lock_remaining -= 1
        else:
            yield state
            if state:
                lock_remaining = lock_count


def generate_times(base_time: dt.datetime, min_seconds: int, max_seconds: int) -> ty.Iterator[dt.datetime]:
    """
    指定した基準時刻から、間隔範囲内でランダムな増分を生成するジェネレータ。

    :param base_time: 基準となる時刻 (datetime オブジェクト)
    :param min_seconds: 増分の最小秒数。
    :param max_seconds: 増分の最大秒数。
    :param steps: 生成する時刻の数。
    :return: ランダムな増分を持つ時刻のイテレータ。
    """
    current_time: dt.datetime = base_time
    while True:
        increment = random.randint(min_seconds, max_seconds)
        current_time += dt.timedelta(seconds=increment)
        yield current_time

def unique_values(values: ty.Iterator[T]) -> ty.Iterator[ty.Optional[T]]:
    """
    Yields unique values from the input iterator, followed by None for subsequent duplicates.
    Args:
        values (ty.Iterator[T]): An iterator of values to process.
    Yields:
        ty.Optional[T]: The next unique value from the input iterator, followed by None for each duplicate.
    """

    for _, iter in it.groupby(values):
        yield next(iter)
        for _ in iter:
            yield None


def _weights_to_percentage_string(weights):
    total = sum(weights)
    percentages = [(w / total) * 100 for w in weights]
    return ", ".join(f"{p:.1f}%" for p in percentages)
