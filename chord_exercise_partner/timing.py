#!/usr/bin/env python3

"""Functions to test platform's timing functions precision and characteristics.
"""

import threading
import time


def check_time_resolution():
    min_step = None
    last_t = time.time()
    for i in range(10):
        now = time.time()
        step = now - last_t
        last_t = now
        if step < 0.0:
            print("Time went backwards!")
            continue
        elif step > 0.0:
            if min_step is None or step < min_step:
                min_step = step
    return min_step

SLEEP_SAMPLES = [ 0.33333, 0.1, 0.033333, 0.01, 0.0033333, 0.001, 0.00033333, 0.0001 ]

def check_sleep_precision():
    cond = threading.Condition()
    report = ["{:^12} {:^20}".format("interval", "error"),
              "{:^12} {:^6} {:^6} {:^6}".format("", "min", "mean", "max")]
    with cond:
        for interval in SLEEP_SAMPLES:
            results = []
            for i in range(10):
                now = time.time()
                target = now + interval
                cond.wait(timeout = interval)
                now = time.time()
                results.append(now - target)
            results.sort()
            min_v = results[0]
            max_v = results[-1]
            mean = sum(results[2:-2]) / (len(results) - 4)
            report.append("{:12.6f} {:^6.3f} {:^6.3f} {:^6.3f}"
                          .format(interval * 1000, min_v * 1000, mean * 1000, max_v * 1000))
    print("Thread sleep precision (ms):\n" + "\n".join(report))

if __name__ == "__main__":
    time_res = check_time_resolution()
    print("Detected time measurement resolution: {:0.6f} ms".format(time_res * 1000))
    check_sleep_precision()
