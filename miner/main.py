import json
import os
import random
import sys
import threading as thrd
import time
from time import perf_counter
from typing import List

import pika
from tabulate import tabulate

from ChallengeMsg import ChallengeMsg
from Client import Client
from ElectionMsg import ElectionMsg
from InitMsg import InitMsg
from PubKeyMsg import PubKeyMsg
from Publisher import Publisher
from RSAKeys import RSAKeys
from SolutionMsg import SolutionMsg
from SystemStatus import SystemStatus
from TransactionBO import TransactionBO
from ValidationStatus import ValidationStatus
from VoteStatus import VoteStatus
from VotingMsg import VotingMsg

transaction_bo = TransactionBO()

systemStatus = SystemStatus.INIT

systemStatusLock = thrd.Lock()
waiting_time = 2

clients_needed = 2

routing_keys = {
    'init_routing_key': 'ppd/init',
    'pub_key_routing_key': 'ppd/pub_key',
    'election_routing_key': 'ppd/election',
    'challenge_routing_key': 'ppd/challenge',
    'solution_routing_key': 'ppd/solution',
    'voting_routing_key': 'ppd/voting'
}


localClient = InitMsg(random.getrandbits(32))

rsaKeys = RSAKeys()

clients: List[Client] = []


class Consumer(thrd.Thread):

    def __init__(self, clients: List[Client], localClient: Client, rsaKeys: RSAKeys, routing_keys: dict):
        thrd.Thread.__init__(self)

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        self.init_routing_key = routing_keys['init_routing_key']
        self.pub_key_routing_key = routing_keys['pub_key_routing_key']
        self.election_routing_key = routing_keys['election_routing_key']
        self.challenge_routing_key = routing_keys['challenge_routing_key']
        self.solution_routing_key = routing_keys['solution_routing_key']
        self.voting_routing_key = routing_keys['voting_routing_key']

        channel.exchange_declare(
            exchange=self.init_routing_key, exchange_type='fanout')
        channel.exchange_declare(
            exchange=self.pub_key_routing_key, exchange_type='fanout')
        channel.exchange_declare(
            exchange=self.election_routing_key, exchange_type='fanout')
        channel.exchange_declare(
            exchange=self.challenge_routing_key, exchange_type='fanout')
        channel.exchange_declare(
            exchange=self.solution_routing_key, exchange_type='fanout')
        channel.exchange_declare(
            exchange=self.voting_routing_key, exchange_type='fanout')

        current_thread_client_suffix = '_client_' + \
            str(localClient.NodeId) + '_thread_' + str(random.getrandbits(64))

        # generating queues for init messages
        queue_name = self.init_routing_key + current_thread_client_suffix
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange=self.init_routing_key,
                           queue=queue_name, routing_key=self.init_routing_key)
        channel.basic_consume(on_message_callback=self.callback_init,
                              queue=queue_name, auto_ack=True)

        # generating queues for public key messages
        queue_name = self.pub_key_routing_key + current_thread_client_suffix
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange=self.pub_key_routing_key,
                           queue=queue_name, routing_key=self.pub_key_routing_key)
        channel.basic_consume(on_message_callback=self.callback_pub_key,
                              queue=queue_name, auto_ack=True)

        # generating queues for election messages
        queue_name = self.election_routing_key + current_thread_client_suffix
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange=self.election_routing_key,
                           queue=queue_name, routing_key=self.election_routing_key)
        channel.basic_consume(on_message_callback=self.callback_election,
                              queue=queue_name, auto_ack=True)

        # generating queues for challenge messages
        queue_name = self.challenge_routing_key + current_thread_client_suffix
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange=self.challenge_routing_key,
                           queue=queue_name, routing_key=self.challenge_routing_key)
        channel.basic_consume(on_message_callback=self.callback_challenge,
                              queue=queue_name, auto_ack=False)

        # generating queues for solution messages
        queue_name = self.solution_routing_key + current_thread_client_suffix
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange=self.solution_routing_key,
                           queue=queue_name, routing_key=self.solution_routing_key)
        channel.basic_consume(on_message_callback=self.callback_solution,
                              queue=queue_name, auto_ack=True)

        # generating queues for voting messages
        queue_name = self.voting_routing_key + current_thread_client_suffix
        channel.queue_declare(queue=queue_name, exclusive=True)
        channel.queue_bind(exchange=self.voting_routing_key,
                           queue=queue_name, routing_key=self.voting_routing_key)
        channel.basic_consume(on_message_callback=self.callback_voting,
                              queue=queue_name, auto_ack=False)

        self.connection = connection
        self.channel = channel
        self.clients = clients
        self.localClient = localClient
        self.rsaKeys = rsaKeys
        self.solutionNodeId = None
        self.voting: List[VotingMsg] = []

    def findClient(self, NodeId: int) -> Client:
        return next(filter(lambda x: x.NodeId == NodeId, self.clients), None)

    def callback_init(self, ch, method, properties, body):
        if systemStatus != SystemStatus.INIT:
            return

        initMsg = InitMsg.deserialize(body)
        client = self.findClient(initMsg.NodeId)
        if client is None:
            client = Client(initMsg.NodeId)
            print("Client " + str(client.NodeId) + " joined")
            self.clients.append(client)

    def callback_pub_key(self, ch, method, properties, body):
        if systemStatus != SystemStatus.PUB_KEYS:
            return

        pubKey = PubKeyMsg.deserialize(body)

        client = self.findClient(pubKey.NodeId)

        if client is None:
            print("Client " + str(pubKey.NodeId) +
                  " tried to send a message without joining")
            return

        if client.PubKey is not None:
            print("Client " + str(pubKey.NodeId) + " already has a public key")
            return

        print("Client " + str(pubKey.NodeId) +
              " published his public key")

        client.PubKey = pubKey.PubKey

    def callback_election(self, ch, method, properties, body):

        if systemStatus != SystemStatus.ELECTION:
            return

        body_dict = json.loads(body)
        client = self.findClient(body_dict['NodeId'])
        if client is None:
            print("Client " + str(body_dict['NodeId']) +
                  " tried to send a message without joining")
            return

        electionMsg = ElectionMsg()
        electionMsg.deserialize(body, client)

        if electionMsg.NodeId == -1:
            return

        if client.ElectionNumber != -1:
            print("Client " + str(client.NodeId) +
                  " already has an election number")
            return

        print("Client " + str(electionMsg.NodeId) +
              " gets number: " + str(electionMsg.ElectionNumber))

        client.ElectionNumber = electionMsg.ElectionNumber

    def callback_challenge(self, ch, method, properties, body):
        global systemStatus

        if systemStatus != SystemStatus.CHALLENGE:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return
        ch.basic_ack(delivery_tag=method.delivery_tag)

        body_dict = json.loads(body)
        client = self.findClient(body_dict['NodeId'])
        if client is None:
            print("Client " + str(body_dict['NodeId']) +
                  " tried to send a message without joining")
            return

        if not client.Leader:
            print("Client " + str(client.NodeId) + " is not a leader")
            return

        challengeMsg = ChallengeMsg()
        challengeMsg.deserialize(body, client)

        if challengeMsg.NodeId == -1:
            return

        print("Transaction " + str(challengeMsg.TransactionNumber) +
              " received with challenge: " + str(challengeMsg.Challenge))

        systemStatusLock.acquire()
        systemStatus = SystemStatus.RUNNING
        systemStatusLock.release()
        transaction_bo.addTransaction(challengeMsg)

    def callback_solution(self, ch, method, properties, body):
        global systemStatus
        if systemStatus == SystemStatus.VOTING:
            return

        body_dict = json.loads(body)
        client = self.findClient(body_dict['NodeId'])
        if client is None:
            print("Client " + str(body_dict['NodeId']) +
                  " tried to send a message without joining")
            return

        solutionMsg = SolutionMsg()
        solutionMsg.deserialize(body, client)

        if solutionMsg.NodeId == -1:
            return

        voting = VotingMsg(self.localClient.NodeId, solutionMsg.TransactionNumber,
                           solutionMsg.Seed)

        validation = transaction_bo.validateChallenge(solutionMsg)
        if(validation == ValidationStatus.VALIDO):
            voting.Vote = VoteStatus.VOTO_SIM

        print("Solution " + solutionMsg.Seed + " for transaction " +
              str(solutionMsg.TransactionNumber) + " is: " + str(voting.Vote))

        systemStatusLock.acquire()
        systemStatus = SystemStatus.VOTING
        systemStatusLock.release()

        self.channel.basic_publish(
            exchange=self.voting_routing_key,  routing_key=self.voting_routing_key, body=voting.serialize(self.rsaKeys))
        self.solutionNodeId = solutionMsg.NodeId

    def callback_voting(self, ch, method, properties, body):
        global systemStatus
        if systemStatus != SystemStatus.VOTING:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return
        ch.basic_ack(delivery_tag=method.delivery_tag)

        body_dict = json.loads(body)
        client = self.findClient(body_dict['NodeId'])
        if client is None:
            print("Client " + str(body_dict['NodeId']) +
                  " tried to send a message without joining")
            return

        votingMsg = VotingMsg()
        votingMsg.deserialize(body, client)

        if votingMsg.NodeId == -1:
            return

        if not any(elem.NodeId == votingMsg.NodeId for elem in self.voting):
            print("Client " + str(votingMsg.NodeId) + " voted")
            self.voting.append(votingMsg)

        if (len(self.voting) == clients_needed):
            result_voting = sum(
                elem.Vote.value for elem in self.voting) > clients_needed / 2
            print("All clients voted, result for the challenger " +
                  str(self.solutionNodeId) + " is:")
            self.voting.sort(key=lambda x: x.NodeId)
            print(tabulate([[vote.NodeId, 'Valid' if vote.Vote == VoteStatus.VOTO_SIM else 'Invalid', vote.TransactionNumber, vote.Seed]
                            for vote in self.voting], headers=['Voter', 'Vote', 'Transaction', 'Seed'], tablefmt='fancy_grid'))

            if (result_voting):
                print("By simple majority the solution is deemed valid")

                transaction = transaction_bo.getTransaction(
                    votingMsg.TransactionNumber)
                transaction.Winner = self.solutionNodeId
                transaction.Seed = votingMsg.Seed

                systemStatusLock.acquire()
                systemStatus = SystemStatus.ELECTION
                systemStatusLock.release()

            else:
                print("Solution invalid")

                systemStatusLock.acquire()
                systemStatus = SystemStatus.RUNNING
                systemStatusLock.release()

            self.voting = []

    def run(self):
        self.channel.start_consuming()


def main():
    publisher = Publisher(routing_keys)

    channel = publisher.channel

    # Join the network
    initState(localClient, routing_keys, clients, channel)

    global systemStatus

    # sharing public keys
    pubKeysState(localClient, routing_keys, clients, channel, rsaKeys)

    # electing leader
    electionState(routing_keys, clients,
                  channel, rsaKeys, localClient)

    max_threads = 3

    threads: List[SeedCalculator] = []

    while True:
        if systemStatus == SystemStatus.RUNNING and len(threads) == 0:
            print("Running for client id: " + str(localClient.NodeId))
            transaction = transaction_bo.getCurrenTransaction()
            for i in range(0, max_threads):
                seed_calculator = SeedCalculator(
                    i, localClient, rsaKeys, routing_keys, transaction.TransactionNumber, transaction.Challenge)
                threads.append(seed_calculator)
                seed_calculator.start()

            for thread in threads:
                thread.join()

            threads = []
        elif systemStatus == SystemStatus.ELECTION:
            threads: List[SeedCalculator] = []
            electionState(routing_keys, clients, channel, rsaKeys, localClient)


def electionState(routing_keys: dict, clients: List[Client], channel, rsaKeys: RSAKeys, localClient: Client):

    global systemStatus
    systemStatusLock.acquire()
    systemStatus = SystemStatus.ELECTION
    systemStatusLock.release()

    electionVote = ElectionMsg(localClient.NodeId)
    election_routing_key = routing_keys['election_routing_key']
    for client in clients:
        client.ElectionNumber = -1
        client.Leader = False

    while any(elem.ElectionNumber == -1 for elem in clients):
        print("Waiting for election")
        channel.basic_publish(
            exchange=election_routing_key,  routing_key=election_routing_key, body=electionVote.serialize(rsaKeys))
        time.sleep(waiting_time)

    channel.basic_publish(
        exchange=election_routing_key,  routing_key=election_routing_key, body=electionVote.serialize(rsaKeys))
    clients.sort(key=lambda x: x.NodeId, reverse=True)
    print("Election Result:")
    print(tabulate([[vote.NodeId, vote.ElectionNumber]
                    for vote in clients], headers=['Id', 'Vote'], tablefmt='fancy_grid'))

    leader = max(clients, key=lambda x: x.ElectionNumber)
    leader.Leader = True

    print("All clients joined, leader is " + str(leader.NodeId))
    print(tabulate([[client.NodeId, 'Leader' if client.Leader else 'Client']
                    for client in clients], headers=['Id', 'Leader'], tablefmt='fancy_grid'))

    print("")
    print("")
    systemStatusLock.acquire()
    systemStatus = SystemStatus.CHALLENGE
    systemStatusLock.release()

    # Sharing the seed for the challenge if the client is the leader
    if (leader.NodeId == localClient.NodeId):
        transaction = transaction_bo.createTransaction()
        challenge_routing_key = routing_keys['challenge_routing_key']
        challengeMsg = ChallengeMsg(
            localClient.NodeId, transaction.TransactionNumber, transaction.Challenge)
        channel.basic_publish(
            exchange=challenge_routing_key,  routing_key=challenge_routing_key, body=challengeMsg.serialize(rsaKeys))

    print("")
    print("")


def pubKeysState(localClient: Client, routing_keys: dict, clients: List[Client], channel, rsaKeys: RSAKeys):
    global systemStatus
    systemStatusLock.acquire()
    systemStatus = SystemStatus.PUB_KEYS
    systemStatusLock.release()

    pub_key_routing_key = routing_keys['pub_key_routing_key']

    pubKey = PubKeyMsg(localClient.NodeId,
                       rsaKeys.public_key.exportKey().decode('utf-8'))

    print("Wait for clients to publish their public keys")
    while any(elem.PubKey is None for elem in clients):
        print("Waiting for public keys")
        channel.basic_publish(
            exchange=pub_key_routing_key,  routing_key=pub_key_routing_key, body=pubKey.serialize())
        time.sleep(waiting_time)

    channel.basic_publish(
        exchange=pub_key_routing_key,  routing_key=pub_key_routing_key, body=pubKey.serialize())
    print("Public keys published")
    print("")
    print("")


def initState(localClient: Client, routing_keys: dict, clients: List[Client], channel):
    init_routing_key = routing_keys['init_routing_key']

    print("Initializing miner for client " + str(localClient.NodeId))
    while len(clients) < clients_needed:
        print("Wait for clients to finish initialization")
        channel.basic_publish(
            exchange=init_routing_key,  routing_key=init_routing_key, body=localClient.serialize())
        time.sleep(waiting_time)

    channel.basic_publish(
        exchange=init_routing_key,  routing_key=init_routing_key, body=localClient.serialize())
    time.sleep(waiting_time)
    print("System initialized")
    print("")
    print("")


class SeedCalculator(thrd.Thread):
    def __init__(self, id: int, localClient: Client, rsaKeys: RSAKeys, routing_keys: dict, transactionNumber: int, challenge: int):
        thrd.Thread.__init__(self)
        self.__time_to_finish = 0
        self.start_time = 0
        self.end_time = 0
        self.__id = id
        self.publisher = Publisher(routing_keys=routing_keys)
        self.solution_routing_key = routing_keys['solution_routing_key']
        self.localClient = localClient
        self.rsaKeys = rsaKeys
        self.transactionNumber = transactionNumber
        self.challenge = challenge

    def run(self):

        print("SeedCalculator {} started".format(self.__id))
        self.start_time = perf_counter()

        while systemStatus == SystemStatus.RUNNING:

            # Calculate the seed
            seed = transaction_bo.generateRandomSeed()
            valid_seed = transaction_bo.verify_seed(
                self.challenge, seed)

            # iterate over prefix characters to check if it is a valid seed
            if (not valid_seed):
                continue
            else:
                # if the prefix is all zeros, the seed is valid and we can break and submit the solution

                submit = SolutionMsg(NodeId=self.localClient.NodeId, TransactionNumber=self.transactionNumber,
                                     Seed=seed)
                submit_json = submit.serialize(self.rsaKeys)

                self.publisher.channel.basic_publish(
                    exchange=self.solution_routing_key,  routing_key=self.solution_routing_key, body=submit_json)

                self.end_time = perf_counter()
                self.__time_to_finish = self.end_time - self.start_time
                print("Solved transaction {} with thread {} in {} seconds".format(
                    self.transactionNumber, self.__id, self.__time_to_finish))


if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("Usage: python3 main.py <number_of_nodes>")
        exit(1)

    print("To exit press CTRL+C")
    clients_needed = int(sys.argv[1])
    consumer = Consumer(clients, localClient, rsaKeys, routing_keys)
    consumer.start()
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')

        consumer.channel.stop_consuming()
        consumer.channel.close()
        consumer.connection.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
