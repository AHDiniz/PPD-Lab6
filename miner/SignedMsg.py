from Client import Client
from RSAKeys import RSAKeys


class SignedMsg:
    def __init__(self) -> None:
        pass

    def serialize(self, key: RSAKeys):
        return key.sign(self.__dict__())

    def deserialize(self, msg_signed: str, client: Client):
        return RSAKeys.verify(msg_signed, client)
