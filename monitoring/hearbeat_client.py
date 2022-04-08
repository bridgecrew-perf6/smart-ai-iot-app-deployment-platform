from kafka import KafkaProducer
import json
import threading
import time
from utils import json_config_loader
KAFKA_SERVERS = json_config_loader('config/kafka.json')['bootstrap_servers']


class HeartBeatClient(threading.Thread):
    def __init__(self, ip, port, flag, system, id, sleep_time=5):
        # system -> application | model
        # system = id for servers and system = container id for
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.flag = flag
        self.system = system
        self.id = id
        self.topic = self.set_topic()
        self.heart_beat_topic = 'heartbeat_stream'
        self.sleep_time = sleep_time
        self.set_producer()
        self._stopevent = threading.Event()

    def set_producer(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVERS, value_serializer=lambda v: v.encode('utf-8'))

    def set_topic(self):
        if self.flag == 0:  # server
            return '{}-{}-{}'.format("server", self.ip, self.port)
        elif self.flag == 1:  # service
            return '{}-{}-{}-{}'.format("service", self.ip, self.port, self.id)
        elif self.flag == 2:  # application
            return '{}-{}-{}-{}'.format("application", self.ip, self.port, self.id)
        else:  # model
            return '{}-{}-{}-{}'.format("model", self.ip, self.port, self.id)

    def get_data(self):
        return f'<*{self.ip}:{self.port} {self}*>'

    def emit(self):
        self.producer.send(self.get_topic(), self.get_data())

    def flush(self, timeout=None):
        self.producer.flush(timeout=timeout)

    def timeout(self):
        time.sleep(self.sleep_time)

    def close(self):
        if self.producer:
            self.producer.close()

    def run(self):
        try:
            while not self._stopevent.isSet():
                self.emit()
                self.timeout()
            self.producer.flush()
        finally:
            self.close()

    def stop(self):
        self._stopevent.set()


# usage:
client = HeartBeatClient()
client.start()
