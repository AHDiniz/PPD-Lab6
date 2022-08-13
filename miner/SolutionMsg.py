
from Client import Client
from SignedMsg import SignedMsg


class SolutionMsg(SignedMsg):
    def __init__(self, NodeID: int = -1, TransactionNumber: int = -1, Seed: str = None) -> None:
        super().__init__()
        self.NodeID = NodeID
        self.TransactionNumber = TransactionNumber
        self.Seed = Seed

    def __dict__(self) -> dict:
        return {
            'NodeID': self.NodeID,
            'TransactionNumber': self.TransactionNumber,
            'Seed': self.Seed
        }

    def deserialize(self, msg_signed: str, client: Client):
        msg_dict = super().deserialize(msg_signed, client)
        if msg_dict is not None:
            self.NodeID = msg_dict["NodeID"]
            self.TransactionNumber = msg_dict["TransactionNumber"]
            self.Seed = msg_dict["Seed"]
