from datetime import datetime, UTC


class IdempotencyService:

    def __init__(self):

        self.seen = {}


    def claim(
        self,
        packet_hash: str
    ):

        if packet_hash in self.seen:
            return False

        self.seen[packet_hash] = datetime.now(UTC)

        return True