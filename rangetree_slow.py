
class RangeTree:
    """
    Slow range tree version, use for testing.
    """
    __slots__ = (
        "_data",
        "_min",
        "_max",
    )

    @classmethod
    def FromRanges(cls, range_iter):
        range_ls = list(range_iter)
        range_ls_unpack = [value for pair in range_ls for value in pair]
        if not range_ls_unpack:
            # empty case
            range_ls_unpack = [0]
        r = RangeTree(min=min(range_ls_unpack), max=max(range_ls_unpack))
        for pair in range_ls:
            for value in range(pair[0], pair[1] + 1):
                r.take(value)
        return r

    def __init__(self, *, min, max):
        self._data = set()
        self._min = 0
        self._max = 0  # not inclusive

    def take(self, value):
        # not essential but OK
        if not self._data and self._min == self._max:
            # Newly created
            self._data.add(value)
            self._min = value
            self._max = value + 1
        else:
            # Existing data
            if value >= self._max:
                self._data.update(set(range(self._max, value + 1)))
                self._max = value + 1
            if value < self._min:
                self._data.update(set(range(value, self._min)))
                self._min = value
        self._data.remove(value)

    def retake(self, value):
        if self.has(value):
            return False
        else:
            self.take(value)
            return True

    def take_any(self):
        if not self._data:
            self._data.add(self._max)
            self._max += 1
        value = min(self._data)
        self.take(value)
        return value

    def release(self, value):
        assert(value not in self._data)
        assert(value >= self._min)
        assert(value <= self._max)
        self._data.add(value)

        # not essential, we could just not do this
        if self.is_empty():
            self._min = 0
            self._max = 0
            self._data = set()

    def is_empty(self):
        return len(self._data) == (self._max - self._min)

    def has(self, value):
        if value < self._min:
            return False
        if value >= self._max:
            return False
        return value not in self._data

    def range_iter(self):
        # Ranges are inclusive
        '''
        Stupid slow code:
        '''
        d = self._data
        i = self._min
        while i < self._max:
            if i not in d:
                i_end = i
                j = i + 1
                while j not in d and j < self._max:
                    i_end = j
                    j += 1
                yield (i, i_end)
                i = j
            else:
                i += 1

