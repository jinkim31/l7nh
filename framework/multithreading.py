import threading
from queue import Queue, Empty
import time
import copy


class ThreadWorker(object):
    def __init__(self, loop_interval=0.0):
        self.__thread = None
        self.__stop_event = threading.Event()
        self.__loop_interval = loop_interval
        self.__loop_interval_lock = threading.Lock()

    def start(self):
        if self.__thread is not None:
            return
        self.__stop_event.clear()
        self.__thread = threading.Thread(target=self.__thread_routine)
        self.__thread.start()

    def stop(self):
        if self.__thread is None:
            return
        self.__stop_event.set()
        self.__thread.join()
        self.__thread = None

    def set_loop_interval(self, loop_interval):
        with self.__loop_interval_lock:
            self.__loop_interval = loop_interval

    def __thread_routine(self):
        self._user_on_start()
        while not self.__stop_event.is_set():
            time_routine_begin = time.time()
            self._user_on_loop()
            time_routine_elapsed = time.time() - time_routine_begin
            with self.__loop_interval_lock:
                loop_interval = self.__loop_interval
            time.sleep(max(0.0, loop_interval - time_routine_elapsed))
        self._user_on_stop()

    def _user_on_start(self):
        pass

    def _user_on_loop(self):
        """
        virtual function that runs in the thread loop. inherit and override.
        """
        raise NotImplementedError()

    def _user_on_stop(self):
        pass


class ItcReceiver(object):
    def __init__(self, queue_size=0):
        self._queue = Queue(maxsize=queue_size)

    def available(self):
        return not self._queue.empty()

    def receive_all(self):
        new_data = []
        while not self._queue.empty():
            new_data.append(self._queue.get())
        return new_data

    def receive(self, timeout=1.0):
        try:
            return self._queue.get(timeout=timeout)
        except Empty:
            return None


class ItcTransmitter(object):
    def __init__(self):
        self.__receiver_queues = []

    def transmit(self, value):
        for receive__queue in self.__receiver_queues:
            if receive__queue.full():
                receive__queue.get()
            receive__queue.put(copy.deepcopy(value))

    def link(self, receiver: ItcReceiver):
        self.__receiver_queues.append(receiver._queue)

    def unlink(self, receiver: ItcReceiver):
        self.__receiver_queues.remove(receiver._queue)
