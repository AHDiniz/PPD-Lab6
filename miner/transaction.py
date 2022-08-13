# define a class for transactions
class Transaction:
    # constructor for the class
    def __init__(self, transactionNumber: int, challenge: int, seed: str, winner: int) -> None:
        self.TransactionNumber = transactionNumber
        self.Challenge = challenge
        self.Seed = seed
        self.Winner = winner

    # override the equals method
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Transaction):
            return False
        return frozenset(self.TransactionNumber) == frozenset(__o.TransactionNumber)

    # override the hash method
    def __hash__(self) -> int:
        return hash(frozenset(self.TransactionNumber))
