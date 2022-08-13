from Client import Client
from SignedMsg import SignedMsg
from VoteStatus import VoteStatus


class VotingMsg(SignedMsg):
    def __init__(self, NodeId: int = -1, TransactionNumber: int = -1, Seed: str = None, Vote: VoteStatus = VoteStatus.VOTO_NAO) -> None:
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
            'Vote': self.Vote.value
        }

    def deserialize(self, msg_signed: str, client: Client):
        msg_dict = super().deserialize(msg_signed, client)
        if msg_dict is not None:
            self.NodeId = msg_dict["NodeId"]
            self.TransactionNumber = msg_dict["TransactionNumber"]
            self.Seed = msg_dict["Seed"]
            self.Vote = VoteStatus(msg_dict["Vote"])
