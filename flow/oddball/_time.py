from __future__ import annotations

import time
from abc import ABC, abstractmethod

from ..utils._docs import copy_doc


class BaseClock(ABC):
    """Base class for high precision clocks.

    If you want to implement a custom clock, you should subclass this class and define
    the abstract method :meth:`stimuli.time.BaseClock.get_time_ns` which should return
    the time elapsed since instantiation in nanoseconds.
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_time_ns(self) -> int:
        """Return the current time in nanoseconds.

        Returns
        -------
        time : int
            The current time in nanoseconds.
        """

    def get_time(self) -> float:
        """Return the current time in seconds.

        Returns
        -------
        time : float
            The current time in seconds.
        """
        return self.get_time_ns() / 1e9


class Clock(BaseClock):
    """Clock which keeps track of time in nanoseconds.

    The origin ``t=0`` corresponds to the instantiation of the
    :class:`stimuli.time.Clock` object. The time is measured either through the
    monotonic :func:`time.monotonic_ns` function or through the performance counter
    :func:`time.perf_counter` function, depending on which one has the highest
    resolution.
    """

    def __init__(self) -> None:
        if (
            time.get_clock_info("perf_counter").resolution
            < time.get_clock_info("monotonic").resolution
        ):
            self._function = time.perf_counter_ns
        else:
            self._function = time.monotonic_ns
        self._t0 = self._function()

    @copy_doc(BaseClock.get_time_ns)
    def get_time_ns(self) -> int:
        return self._function() - self._t0


def sleep(duration: float, *, clock: BaseClock = Clock) -> None:
    """High precision sleep function.

    Parameters
    ----------
    duration : float
        Duration to sleep in seconds. If the value is less than or equal to 0, the
        function returns immediately.
    clock : BaseClock
        Clock object to use for time measurement. By default, the
        :class:`stimuli.time.Clock` class is used.

    Notes
    -----
    On Windows, only python version 3.11 and above have good accuracy when sleeping.
    This accuracy limitation dictates the minimum version of ``stimuli``.
    """
    if duration <= 0:
        return
    clock = clock()
    duration = int(duration * 1e9)
    while True:
        remaining_time = duration - clock.get_time_ns()  # nanoseconds
        if remaining_time <= 0:
            break
        if remaining_time >= 200000:  # 200 microseconds
            time.sleep(remaining_time * 1e-9 / 2)
