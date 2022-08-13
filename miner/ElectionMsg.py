import random
from Client import Client
from SignedMsg import SignedMsg


class ElectionMsg(SignedMsg):
    def __init__(self, NodeId: int = -1) -> None:
        super().__init__()
        self.NodeId = NodeId
        self.ElectionNumber = random.getrandbits(32)

    def __dict__(self) -> dict:
        return {
            'NodeId': self.NodeId,
            'ElectionNumber': self.ElectionNumber
        }

    def deserialize(self, msg_signed: str, client: Client):
        msg_dict = super().deserialize(msg_signed, client)
        if msg_dict is not None:
            self.NodeId = msg_dict["NodeId"]
            self.ElectionNumber = msg_dict["ElectionNumber"]
