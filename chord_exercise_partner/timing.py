#!/usr/bin/env python3

"""Functions to test platform's timing functions precision and characteristics.
"""

import threading
import time

def check_time_resolution(func=time.time):
    """Check resolution of a time measuring function.

    Returns the smallest change in function value detected."""
    min_step = None
    last_t = func()
    for _ in range(10):
        while True:
            now = func()
            step = now - last_t
            last_t = now
            if step < 0.0:
                print("Time went backwards!")
                break
            elif step > 0.0:
                if min_step is None or step < min_step:
                    min_step = step
                break
    return min_step

SLEEP_SAMPLES = [0.033333, 0.01, 0.0033333, 0.001, 0.00033333, 0.0001]

def check_sleep_precision():
    """Measure threading.Condition.wait() time precision."""
    cond = threading.Condition()
    report = ["{:^12} {:^20}".format("interval", "error"),
              "{:^12} {:^6} {:^6} {:^6}".format("", "min", "mean", "max")]
    with cond:
        for interval in SLEEP_SAMPLES:
            results = []
            for _ in range(10):
                now = time.perf_counter()
                target = now + interval
                cond.wait(timeout=interval)
                now = time.perf_counter()
                results.append(now - target)
            results.sort()
            min_v = results[0]
            max_v = results[-1]
            mean = sum(results[2:-2]) / (len(results) - 4)
            report.append("{:12.6f} {:^6.3f} {:^6.3f} {:^6.3f}"
                          .format(interval * 1000, min_v * 1000, mean * 1000, max_v * 1000))
    print("Thread sleep precision (ms):\n" + "\n".join(report))

if __name__ == "__main__":
    # pylint: disable=invalid-name
    time_res = check_time_resolution(time.time)
    print("Detected time measurement resolution: {:0.6f} ms".format(time_res * 1000))
    time_res = check_time_resolution(time.perf_counter)
    print("Detected precise time measurement resolution: {:0.6f} ms".format(time_res * 1000))
    check_sleep_precision()
