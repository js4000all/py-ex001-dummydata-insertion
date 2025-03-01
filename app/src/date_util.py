import datetime as dt
import time
import typing as ty

def execute_at(
        t: dt.datetime, 
        f: ty.Callable[..., ty.Any],
        get_now: ty.Callable[[], dt.datetime] = dt.datetime.now,
        sleep: ty.Callable[[int], ty.Any] = time.sleep
        ) -> None:
    now = get_now()
    delay: int = int((t - now).total_seconds())
    if delay > 0:
        print(f'delay={delay} ({t} <- {now})')
        sleep(delay)
    f()
