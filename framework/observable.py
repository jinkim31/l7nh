
class Observable(object):
    """
    Observable class that implements observer pattern.
    Not thread safe.
    """
    def __init__(self, value=None):
        self._value = value
        self.__observers = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._notify_observers()

    def observe(self, observer, notify_now=False):
        self.__observers.append(observer)
        if notify_now:
            observer(self._value)

    def _notify_observers(self):
        for observer in self.__observers:
            observer(self._value)

class ObservableList(Observable):
    """
    Observable class that implements observer pattern.
    Not thread safe.
    """
    def __init__(self):
        super().__init__([])


    def append(self, x):
        self._value.append(x)
        self._notify_observers()

    def len(self):
        return len(self._value)

    def clear(self):
        self._value = []
        self._notify_observers()


