from Client import Client
from SignedMsg import SignedMsg


class ChallengeMsg(SignedMsg):
    def __init__(self, NodeId: int = -1, TransactionNumber: int = -1, Challenge: int = -1) -> None:
        super().__init__()
        self.NodeId = NodeId
        self.TransactionNumber = TransactionNumber
        self.Challenge = Challenge

    def __dict__(self) -> dict:
        return {
            "NodeId": self.NodeId,
            "TransactionNumber": self.TransactionNumber,
            "Challenge": self.Challenge
        }

    def deserialize(self, msg_signed: str, client: Client):
        msg_dict = super().deserialize(msg_signed, client)
        if msg_dict is not None:
            self.NodeId = msg_dict["NodeId"]
            self.TransactionNumber = msg_dict["TransactionNumber"]
            self.Challenge = msg_dict["Challenge"]
