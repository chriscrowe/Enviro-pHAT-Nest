class RollingAverage(object):

    def __init__(self, window_size):
        self.window_size = window_size
        self.values = []

    @property
    def is_full(self):
        return len(self.values) == self.window_size

    def add_val(self, value):
        self.values.append(value)
        while len(self.values) > self.window_size:
            del self.values[0]

    def get_average(self):
        return sum(self.values) / float(len(self.values))