
class ViewEvent(object):
    def __init__(self):
        self.__listeners = []

    def listen(self, callback):
        self.__listeners.append(callback)

    def fire(self, args=None):

        for listener in self.__listeners:
            if args is not None:
                listener(args)
            else:
                listener()