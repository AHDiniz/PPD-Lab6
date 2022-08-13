from PubKeyMsg import PubKeyMsg
from RSAKeys import RSAKeys


class SignedMsg:
    def __init__(self) -> None:
        pass

    def serialize(self, key: RSAKeys):
        return key.sign(self.__dict__())

    def deserialize(msg_signed: str, pub_key: PubKeyMsg):
        return RSAKeys.verify(msg_signed, pub_key.PubKey)
