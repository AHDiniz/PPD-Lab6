from typing import List

from tabulate import tabulate

from transaction import Transaction

transactions: List[Transaction] = []


class TransactionDAO:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # add a transaction to the list of transactions
    def createTransaction(self, challenge) -> Transaction:
        transaction = Transaction(
            self.getLastTransaction().TransactionNumber + 1, challenge, None, -1)

        self.addTransaction(transaction)
        return transaction

    # get a transaction by id
    def getTransaction(self, transaction_id: int) -> Transaction:
        for transaction in transactions:
            if transaction.TransactionNumber == transaction_id:
                return transaction

    # add transaction to the list of transactions
    def addTransaction(self, transaction: Transaction) -> None:
        if (not any(elem.TransactionNumber == transaction.TransactionNumber for elem in transactions)):
            transactions.append(transaction)
            self.printTransactions()

    # get last transaction
    def getLastTransaction(self) -> Transaction:
        if len(transactions) == 0:
            return Transaction(-1, 0, None, -1)  # default transaction

        return transactions[-1]

    # print all transactions
    def printTransactions(self) -> None:
        print(tabulate([[transaction.TransactionNumber, transaction.Challenge, transaction.Seed, transaction.Winner]
              for transaction in transactions], headers=['Transaction ID', 'Challenge', 'Seed', 'Winner (Node Id)'], tablefmt='fancy_grid'))
        print("")
