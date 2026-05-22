import time
import uuid
from decimal import Decimal
from schemas import (MeshPacket,PaymentInstruction)
from crypto import encrypt_payload

class DemoService:
    def create_packet(self,sender: str,receiver: str,amount: Decimal,pin_hash: str):
        instruction = PaymentInstruction(
            sender=sender,
            receiver=receiver,
            amount=amount,
            pin_hash=pin_hash,
            nonce=str(uuid.uuid4()),
            signed_at=int(time.time() * 1000)
        )
        payload = instruction.model_dump_json()
        ciphertext = encrypt_payload(payload.encode())

        packet = MeshPacket(
            packet_id=str(uuid.uuid4()),
            ttl=5,
            created_at=int(time.time() * 1000),
            ciphertext=ciphertext
        )

        return packet
