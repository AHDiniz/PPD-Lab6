import hashlib
import random
import string
from ChallengeMsg import ChallengeMsg
from SolutionMsg import SolutionMsg
from ValidationStatus import ValidationStatus
from TransactionDAO import TransactionDAO
from transaction import Transaction


class TransactionBO:

    characters = string.ascii_letters + string.digits + string.punctuation

    def __init__(self):
        self.transactionDAO = TransactionDAO()

    # Create transaction
    def createTransaction(self) -> Transaction:
        transaction = self.transactionDAO.createTransaction(
            random.randint(20, 40))
        return transaction

    def addTransaction(self, challengeMsg: ChallengeMsg) -> None:
        transaction = Transaction(challengeMsg.TransactionNumber,
                                  challengeMsg.Challenge, None, -1)
        self.transactionDAO.addTransaction(transaction)

    def getTransaction(self, id) -> Transaction:
        return self.transactionDAO.getTransaction(id)

    def getCurrenTransaction(self) -> Transaction:
        return self.transactionDAO.getLastTransaction()

    # submit a seed for the transaction given by id and return if it is valid or not, -1 if not found
    def validateChallenge(self, solutionMsg: SolutionMsg) -> ValidationStatus:

        transactionNumber: int = solutionMsg.TransactionNumber
        seed: str = solutionMsg.Seed
        nodeId: int = solutionMsg.NodeId
        transaction = self.transactionDAO.getTransaction(transactionNumber)
        if transaction is None:
            return ValidationStatus.ID_INVALIDO

        if transaction.Seed is not None:
            return ValidationStatus.JA_SOLUCIONADO

        if (self.verify_seed(transaction.Challenge, seed)):
            # mark the transaction as solved and the winner, return valid
            transaction.Seed = seed
            transaction.Winner = nodeId
            return ValidationStatus.VALIDO

        return ValidationStatus.INVALIDO

    # validate seed of challenge
    def verify_seed(self, challenge: int, seed: str) -> bool:
        hashByte = hashlib.sha1(str.encode(seed, 'ascii')).digest()
        prefix = self.bitsof(hashByte, challenge)

        # iterate over prefix characters to check if it is a valid seed
        if (prefix != 0):
            return False

        return True

    def bitsof(self, bt, nbits):
        # Directly convert enough bytes to an int to ensure you have at least as many bits
        # as needed, but no more
        neededbytes = (nbits+7)//8
        if neededbytes > len(bt):
            raise ValueError(
                "Require {} bytes, received {}".format(neededbytes, len(bt)))
        i = int.from_bytes(bt[:neededbytes], 'big')
        # If there were a non-byte aligned number of bits requested,
        # shift off the excess from the right (which came from the last byte processed)
        if nbits % 8:
            i >>= 8 - nbits % 8
        return i

    def generateRandomSeed(self):
        return ''.join(random.choice(self.characters) for _ in range(30))
