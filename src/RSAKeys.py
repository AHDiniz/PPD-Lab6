
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import subprocess
import json

from PubKeyMsg import PubKeyMsg


class RSAKeys():
    def __init__(self) -> None:

        # Generate a new RSA key pair.
        subprocess.run(["./generate_key.sh"])
        with open("private_key.pem", "r") as src:
            self.private_key = RSA.importKey(src.read())
        self.public_key = self.private_key.publickey()

    # Function for signing a message and returning its content for the queue.
    def sign(self, msg: dict) -> str:
        msg_json = json.dumps(msg, ensure_ascii=True)
        # This is the signature.
        h = SHA256.new(msg_json.encode('ascii'))
        signer = PKCS1_v1_5.new(self.private_key)
        signature = signer.sign(h)

        msg.update({"Sign", signature.hex()})

        msg_json = json.dumps(msg, ensure_ascii=True)

        return msg_json

    # Function for verifying a message and returning its content for the processing, if it is valid.
    # If it is not valid, it returns None.
    def verify(msg_signed: str, pub_key: PubKeyMsg) -> dict:
        msg_dict: dict = json.loads(msg_signed, ensure_ascii=True)

        signature = bytes.fromhex(msg_dict.pop("Sign"))

        msg_json = json.dumps(msg_dict, ensure_ascii=True)

        digest = SHA256.new(msg_json.encode('ascii'))

        verifier = PKCS1_v1_5.new(pub_key.PubKey)

        verified = verifier.verify(digest, signature)

        if verified:
            return msg_dict
        else:
            return None
