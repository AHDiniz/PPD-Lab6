
import threading as thrd
import pika


class Publisher():
    def __init__(self, routing_keys: dict):
        thrd.Thread.__init__(self)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(
            exchange=routing_keys['init_routing_key'], exchange_type='fanout')
        channel.exchange_declare(
            exchange=routing_keys['pub_key_routing_key'], exchange_type='fanout')
        channel.exchange_declare(
            exchange=routing_keys['election_routing_key'], exchange_type='fanout')
        channel.exchange_declare(
            exchange=routing_keys['challenge_routing_key'], exchange_type='fanout')
        channel.exchange_declare(
            exchange=routing_keys['solution_routing_key'], exchange_type='fanout')
        channel.exchange_declare(
            exchange=routing_keys['voting_routing_key'], exchange_type='fanout')

        self.connection = connection
        self.channel = channel
