class Client():
    def __init__(self, NodeId: int = -1) -> None:
        self.NodeId = NodeId
        self.PubKey = None
        self.ElectionNumber = -1
        self.Leader = False
    
    def __eq__(self, other):
        if isinstance(other, Client):
            return self.NodeId == other.NodeId
        return False
