from collections import namedtuple
from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError

# ZKKafkaTopic = namedtuple('ZKKafkaTopic', ['topic'])
# ZKKafkaTopic = namedtuple('ZKKafkaTopic', ['topic', 'broker', 'num_partitions'])


class ZKClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = KazooClient(hosts=':'.join([host, str(port)]))

    @classmethod
    def _zjoin(cls, e):
        return '/'.join(e)

    def kafka_topics(self, broker_root='/brokers'):
        '''
        Returns a list of ZKKafkaTopic tuples, where each tuple represents a topic being stored in a broker.
        '''

        topics = []
        t_root = self._zjoin([broker_root, 'topics'])

        self.client.start()
        try:
            for t in self.client.get_children(t_root):
                topics.append(t)
                # topics.append(ZKKafkaTopic._make([t]))
                # for b in self.client.get_children(self._zjoin([t_root, t])):
                #     n = self.client.get(self._zjoin(t_root, t, b))[0]
                #     topics.append(ZKKafkaTopic._make([t, b, n]))
        except NoNodeError:
            raise ZKError('Topic nodes do not exist in ZooKeeper')
        self.client.stop()

        return topics


class ZKError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg