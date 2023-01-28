from threading import Lock


class Lamport_clock:
    def __init__(self, lc=0):
        self.time = lc
        self.lock = Lock()

    def get_time(self):
        return self.time

    def set_time(self, set_time):
        with self.lock:
            self.time = set_time

    def tick(self):
        with self.lock:
            self.time += 1

    def send_event(self):
        with self.lock:
            self.time += 1
            return self.time

    def receive_event(self, sender_time):
        with self.lock:
            self.time = max(self.time, sender_time) + 1
