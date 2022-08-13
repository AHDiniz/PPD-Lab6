from PubKeyMsg import PubKeyMsg
from SignedMsg import SignedMsg


class ChallengeMsg(SignedMsg):
    def __init__(self, NodeId: int, TransactionNumber: int, Challenge: int) -> None:
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

    def deserialize(msg_signed: str, pub_key: PubKeyMsg):
        msg_dict = super().deserialize(msg_signed, pub_key)
        if msg_dict is not None:
            return ChallengeMsg(msg_dict["NodeId"], msg_dict["TransactionNumber"], msg_dict["Challenge"])
        return None
