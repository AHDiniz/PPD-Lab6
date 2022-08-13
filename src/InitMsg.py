import json


class InitMsg():
    def __init__(self, NodeId: int) -> None:
        self.NodeId = NodeId

    def __dict__(self) -> dict:
        return {
            'NodeId': self.NodeId
        }

    def serialize(self):
        return json.dumps(self.__dict__(), ensure_ascii=True)

    def deserialize(msg: str):
        msg_dict = json.loads(msg)
        return InitMsg(msg_dict["NodeId"])
