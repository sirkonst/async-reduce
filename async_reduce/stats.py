import statistics
from typing import Sequence
import math


class AggregatedStats:
    _n = 0
    _mu = _mu2 = _min = _max = 0.0

    def __init__(self, data: Sequence[float] = None):
        if data:
            self._n = len(data)
            self._mu = statistics.mean(data)
            self._mu2 = statistics.mean((x ** 2 for x in data))
            self._min = min(data)
            self._max = max(data)

    @property
    def n(self) -> int:
        return self._n

    @property
    def min(self) -> float:
        return self._min

    @property
    def max(self) -> float:
        return self._max

    @property
    def mean(self) -> float:
        return self._mu

    @property
    def pvariance(self) -> float:
        return self._mu2 - self._mu ** 2

    @property
    def pstd(self) -> float:
        return math.sqrt(self.pvariance)

    @property
    def variance(self) -> float:
        return (self._mu2 - self._mu ** 2) * (self._n / (self._n - 1))

    @property
    def std(self) -> float:
        return math.sqrt(self.variance)

    def consume(self, *data: float):
        if data:
            k = len(data)
            sm = sum(data)
            sm2 = sum((x ** 2 for x in data))
            self._min = min(self._min, *data)
            self._max = max(self._max, *data)
            self._mu = (self._mu * self._n + sm) / (k + self._n)
            self._mu2 = (self._mu2 * self._n + sm2) / (k + self._n)
            self._n += k
