import json


class PubKeyMsg():
    def __init__(self, NodeId: int, PubKey: str) -> None:
        self.NodeId = NodeId
        self.PubKey = PubKey

    def __dict__(self) -> dict:
        return {
            'NodeId': self.NodeId,
            'PubKey': self.PubKey
        }

    def serialize(self):
        return json.dumps(self.__dict__(), ensure_ascii=True)

    def deserialize(msg: str):
        msg_dict = json.loads(msg)
        return PubKeyMsg(msg_dict["NodeId"], msg_dict["PubKey"])
