from sqlalchemy.exc import IntegrityError

from models import (
    Account,
    Transaction
)


class SettlementService:

    def __init__(self, db):

        self.db = db


    def settle(
        self,
        instruction,
        packet_hash
    ):

        sender = (
            self.db.query(Account)
            .filter(
                Account.owner == instruction.sender
            )
            .first()
        )

        receiver = (
            self.db.query(Account)
            .filter(
                Account.owner == instruction.receiver
            )
            .first()
        )

        if not sender or not receiver:

            return {
                "outcome": "INVALID",
                "packet_hash": packet_hash,
                "reason": "Account not found"
            }

        if sender.balance < instruction.amount:

            return {
                "outcome": "REJECTED",
                "packet_hash": packet_hash,
                "reason": "Insufficient balance"
            }

        sender.balance -= instruction.amount

        receiver.balance += instruction.amount

        tx = Transaction(
            packet_hash=packet_hash,
            sender=instruction.sender,
            receiver=instruction.receiver,
            amount=instruction.amount,
            status="SETTLED"
        )

        self.db.add(tx)

        try:

            self.db.commit()

        except IntegrityError:

            self.db.rollback()

            return {
                "outcome": "DUPLICATE_DROPPED",
                "packet_hash": packet_hash
            }

        self.db.refresh(tx)

        return {
            "outcome": "SETTLED",
            "packet_hash": packet_hash,
            "transaction_id": tx.id
        }