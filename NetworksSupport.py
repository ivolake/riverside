import random


class Jitter:
    def __init__(self, low: float, high: float,
                 accuracy: int = 0):
        if low < 0:
            raise ValueError('Low limit must be greater then zero.')

        self.low = low
        self.high = high

        self._additional_power = accuracy

    def __repr__(self):
        return f'Jitter function with low={self.low}, high={self.high}'

    def __call__(self) -> float:
        return random.randrange(self._low, self._high)/self._order_multiplier

    @property
    def _order_multiplier(self):
        i = len(str(self.high).replace('.', ''))
        return 10**(i - 1 + self._additional_power)

    @property
    def _low(self):
        return int(self.low * self._order_multiplier)

    @property
    def _high(self):
        return int(self.high * self._order_multiplier)

class RandomJitter(Jitter):
    def __init__(self, lowest_low: float, highest_low: float,
                 lowest_high: float, highest_high: float,
                 accuracy: int = 2):

        if lowest_low > lowest_high:
            raise ValueError('Lowest low level cannot be greater than lowest high.')

        if highest_low > highest_high:
            raise ValueError('Highest low level cannot be greater than highest high.')

        self.lowest_low = lowest_low
        self.highest_low = highest_low
        self.lowest_high = lowest_high
        self.highest_high = highest_high

        self._additional_power = accuracy

        super().__init__(self._random_low, self._random_high)

    @property
    def _highest_low_order_multiplier(self):
        i = len(str(self.highest_low).replace('.', ''))
        return 10 ** (i - 1 + self._additional_power)

    @property
    def _highest_high_order_multiplier(self):
        i = len(str(self.highest_high).replace('.', ''))
        return 10 ** (i - 1 + self._additional_power)

    @property
    def _random_low(self):
        return random.randrange(self.lowest_low * self._highest_low_order_multiplier,
                                self.highest_low * self._highest_low_order_multiplier) \
               / self._highest_low_order_multiplier

    @property
    def _random_high(self):
        return random.randrange(self.lowest_high * self._highest_high_order_multiplier,
                                self.highest_high * self._highest_high_order_multiplier) \
               / self._highest_high_order_multiplier


class ReceivedMessageReport:
    def __init__(self):
        ...