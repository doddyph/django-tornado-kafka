import json
import time
import signal

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.utils.importlib import import_module
import os
import django
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define, options
from tornado.web import Application, FallbackHandler, RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler, WebSocketClosedError
from tornado.wsgi import WSGIContainer
from kafka_usage import Consumer, Producer
from zkclient import ZKClient


define('wshost', type=str, default="localhost")
define('wsport', type=int, default=8080)
define('kafkahost', type=str, default="localhost")
define('kafkaport', type=int, default=9092)
define('zkhost', type=str, default="localhost")
define('zkport', type=int, default=2181)
define('debug', type=bool, default=False)

subscriptions = {}
kafka_topics = []


class HelloTornado(RequestHandler):
    def get(self):
        self.write('Hello from Tornado')


class WSHandler(WebSocketHandler):
    def open(self):
        self.user = self.get_django_current_user()
        print '[WebSocket] New connection from user: {}.'.format(self.user)
        self.write_message(json.dumps({'topic': kafka_topics}))

    def on_message(self, message):
        # self.user = self.get_django_current_user()
        print '[WebSocket] Receive: {0} from user: {1}'.format(message, self.user)
        j_decoded = json.loads(message)
        action = j_decoded['action']

        if action == 'start':
            self.on_start(self.user)
        elif action == 'stop':
            self.on_stop(self.user)

    def send_message(self, message):
        # self.user = self.get_django_current_user()
        print '[WebSocket] Sent: {0} to user: {1}'.format(message, self.user)
        try:
            self.write_message(message)
        except WebSocketClosedError:
            print '[WebSocket] WebSocketClosedError'
            self.on_stop(self.user)

    def on_close(self):
        print '[WebSocket] Connection closed'

    def on_start(self, user):
        if str(user) in subscriptions.keys():
            t = subscriptions[str(user)]
        else:
            t = Consumer(args=(options.kafkahost, options.kafkaport, str(kafka_topics[0])))
            subscriptions[str(user)] = t
            t.setDaemon(True)
            t.start()

        t.add_subscriber(self)

    def on_stop(self, user):
        if str(user) in subscriptions.keys():
            t = subscriptions[str(user)]
            t.remove_subscriber(self)
            count = t.get_subscribers_length()
            print '[WebSocket] On stop, subscriber count: {}'.format(count)

            if count == 0:
                t.stop_consumer()
                del subscriptions[str(user)]

    def get_django_current_user(self):
        class Dummy(object):
            pass
        django_request = Dummy()
        django_request.session = self.get_django_session()

        if django_request.session is not None:
            try:
                user_id = django_request.session['_auth_user_id']
                return user_id
            except KeyError:
                print '[WebSocket] KeyError'
                self.close()

        return None
    #     user = get_user(django_request)
    #
    #     if user.is_authenticated():
    #         return user
    #     else:
    #         if not self.request.headers.has_key('Authorization'):
    #             return None
    #
    #         kind, data = self.request.headers['Authorization'].split(' ')
    #         if kind != 'Basic':
    #             return None
    #
    #         (username, _, password) = data.decode('base64').partition(':')
    #         user = authenticate(username=username, password=password)
    #         if user is not None and user.is_authenticated():
    #             return user
    #
    #     return None

    def get_django_session(self):
        if not hasattr(self, '_session'):
            session_key = self.get_cookie(settings.SESSION_COOKIE_NAME)
            print '[WebSocket] Session key: {}'.format(session_key)
            session_engine = import_module(settings.SESSION_ENGINE)
            session = session_engine.SessionStore(session_key)
            return session
        return None

    # def get_django_request(self):
    #     request = WSGIRequest(WSGIContainer.environ(self.request))
    #     request.session = self.get_django_session()
    #
    #     if self.current_user:
    #         request.user = self.current_user
    #     else:
    #         request.user = AnonymousUser()
    #
    #     return request


class WSApplication(Application):
    def __init__(self):
        wsgi_app = get_wsgi_application()
        wsgi_container = WSGIContainer(wsgi_app)

        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=options.debug,
        )
        handlers = [
            (r'/hello-tornado', HelloTornado),
            (r'/ws', WSHandler),
            (r'/static/(.*)', StaticFileHandler, dict(path=settings['static_path'])),
            (r'.*', FallbackHandler, dict(fallback=wsgi_container)),
        ]
        Application.__init__(self, handlers, **settings)


def shutdown(server):
    ioloop = IOLoop.instance()
    print '[WebSocket] Stopping server...'
    server.stop()

    def finalize():
        ioloop.stop()
        print '[WebSocket] Server stopped'

    ioloop.add_timeout(time.time() + 1.5, finalize)


def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'project_dj.settings'
    # print 'django version: {0}, {1}'.format(django.VERSION, django.VERSION[1])
    if django.VERSION[1] > 5:
        django.setup()
    parse_command_line()

    http_server = HTTPServer(WSApplication())
    http_server.listen(options.wsport, address=options.wshost)
    signal.signal(signal.SIGINT, lambda sig, frame: shutdown(http_server))

    zk = ZKClient(options.zkhost, options.zkport)
    global kafka_topics
    kafka_topics = zk.kafka_topics()

    t = Producer(args=(options.kafkahost, options.kafkaport, str(kafka_topics[0])))
    t.setDaemon(True)
    t.start()

    print '[WebSocket] Starting server on {0}:{1}/ws'.format(options.wshost, options.wsport)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()