from PubKeyMsg import PubKeyMsg
from SignedMsg import SignedMsg


class VotingMsg(SignedMsg):
    def __init__(self, NodeId: int, TransactionNumber: int, Seed: str, Vote: int) -> None:
        super().__init__()
        self.NodeId = NodeId
        self.TransactionNumber = TransactionNumber
        self.Seed = Seed
        self.Vote = Vote

    def __dict__(self) -> dict:
        return {
            'NodeId': self.NodeId,
            'TransactionNumber': self.TransactionNumber,
            'Seed': self.Seed,
            'Vote': self.Vote
        }

    def deserialize(msg_signed: str, pub_key: PubKeyMsg):
        msg_dict = super().deserialize(msg_signed, pub_key)
        if msg_dict is not None:
            return VotingMsg(msg_dict["NodeId"], msg_dict["TransactionNumber"], msg_dict["Seed"], msg_dict["Vote"])
        return None
