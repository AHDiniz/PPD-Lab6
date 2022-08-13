from PubKeyMsg import PubKeyMsg
from SignedMsg import SignedMsg


class ElectionMsg(SignedMsg):
    def __init__(self, NodeId: int, ElectionNumber: int) -> None:
        super().__init__()
        self.NodeId = NodeId
        self.ElectioNumber = ElectionNumber

    def __dict__(self) -> dict:
        return {
            'NodeId': self.NodeId,
            'ElectionNumber': self.ElectionNumber
        }

    def deserialize(msg_signed: str, pub_key: PubKeyMsg):
        msg_dict = super().deserialize(msg_signed, pub_key)
        if msg_dict is not None:
            return ElectionMsg(msg_dict["NodeId"], msg_dict["ElectionNumber"])
        return None
