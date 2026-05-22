from pydantic import BaseModel
from decimal import Decimal

class PaymentInstruction(BaseModel):
    sender: str
    receiver: str
    amount: Decimal
    nonce: str
    signed_at: int

class MeshPacket(BaseModel):
    packet_id: str
    ttl: int
    created_at: int
    ciphertext: str
