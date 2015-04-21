from functools import partial
import json
import random
from threading import Thread
from kafka import KafkaClient, SimpleConsumer, SimpleProducer
import time
from tornado.ioloop import IOLoop


class Consumer(Thread):
    def __init__(self, args=()):
        super(Consumer, self).__init__()
        self.host = args[0]
        self.port = args[1]
        self.topic = args[2]
        print '[KafkaConsumer] host: {0}, port: {1}, topic: {2}'.format(self.host, self.port, self.topic)
        self.consumer = None
        self.consumer_keep_run = True
        self.consumer_paused = False
        self.consumer_subscribers = []

    def run(self):
        client = kafka_client(self.host, self.port)
        self.consumer = SimpleConsumer(client, None, self.topic)
        self.consumer.seek(0, 1)

        while self.consumer_keep_run:
            print '[KafkaConsumer] looping..'
            if not self.consumer_paused:
                for message in self.consumer.get_messages(block=False):
                    offset = message.offset
                    value = message.message.value
                    j_encoded = json.dumps({'offset': offset, 'message': value})
                    print '[KafkaConsumer] {}'.format(j_encoded)

                    for subscriber in self.consumer_subscribers:
                        IOLoop.instance().add_callback(partial(subscriber.send_message, j_encoded))
            time.sleep(1)

    def pause_consumer(self, paused):
        self.consumer_paused = paused

    def stop_consumer(self):
        self.consumer_keep_run = False

    def add_subscriber(self, subscriber):
        self.consumer_subscribers.append(subscriber)

    def remove_subscriber(self, subscriber):
        self.consumer_subscribers.remove(subscriber)

    def get_subscribers_length(self):
        length = len(self.consumer_subscribers)
        return length

    def get_subscribers(self):
        return self.subscribers


class Producer(Thread):
    def __init__(self, args=()):
        super(Producer, self).__init__()
        self.host = args[0]
        self.port = args[1]
        self.topic = args[2]
        print '[KafkaProducer] host: {0}, port: {1}, topic: {2}'.format(self.host, self.port, self.topic)
        self.producer = None
        self.producer_keep_run = True

    def run(self):
        client = kafka_client(self.host, self.port)
        self.producer = SimpleProducer(client)

        while self.producer_keep_run:
            randnum = random.randrange(10)
            print '[KafkaProducer] Number: {}'.format(randnum)
            self.producer.send_messages(self.topic, str(randnum))
            time.sleep(1)

    def stop_producer(self):
        self.producer_keep_run = False


def kafka_client(host, port):
    brokers = ':'.join([host, str(port)])
    client = KafkaClient(brokers)
    return client
