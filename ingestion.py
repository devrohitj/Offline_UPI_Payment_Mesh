import json

from datetime import (
    datetime,
    timedelta,
    UTC
)

from schemas import PaymentInstruction

from crypto import (
    decrypt_payload,
    hash_ciphertext
)


class BridgeIngestionService:

    def __init__(
        self,
        settlement_service,
        idempotency_service
    ):

        self.settlement_service = settlement_service

        self.idempotency_service = idempotency_service


    def ingest(self, packet):

        try:

            packet_hash = hash_ciphertext(
                packet.ciphertext
            )

            claimed = self.idempotency_service.claim(
                packet_hash
            )

            if not claimed:

                return {
                    "outcome": "DUPLICATE_DROPPED",
                    "packet_hash": packet_hash
                }

            plaintext = decrypt_payload(
                packet.ciphertext
            )

            data = json.loads(
                plaintext.decode()
            )

            instruction = PaymentInstruction(
                **data
            )

            signed_time = datetime.fromtimestamp(
                instruction.signed_at / 1000,
                tz=UTC
            )

            now = datetime.now(UTC)

            if now - signed_time > timedelta(hours=24):

                return {
                    "outcome": "INVALID",
                    "packet_hash": packet_hash,
                    "reason": "Packet expired"
                }

            return self.settlement_service.settle(
                instruction,
                packet_hash
            )

        except Exception as e:

            return {
                "outcome": "INVALID",
                "packet_hash": hash_ciphertext(
                    packet.ciphertext
                ),
                "reason": str(e)
            }