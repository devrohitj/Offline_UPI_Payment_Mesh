from decimal import Decimal
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from fastapi import (
    FastAPI,
    Depends,
    Request
)

from sqlalchemy.orm import Session

from models import (
    SessionLocal,
    get_db,
    Account,
    Transaction
)

from settlement import SettlementService

from idempotency import IdempotencyService

from ingestion import BridgeIngestionService

from demo import DemoService

from mesh import MeshNetwork

templates = Jinja2Templates(
    directory="templates"
)

# ---------------------------------------------------
# FastAPI application
# ---------------------------------------------------

app = FastAPI()


# ---------------------------------------------------
# Global singleton services
# ---------------------------------------------------

mesh = MeshNetwork()

demo_service = DemoService()

idempotency_service = IdempotencyService()


# ---------------------------------------------------
# Seed initial demo accounts
# ---------------------------------------------------

def seed_accounts():

    db = SessionLocal()

    try:

        existing = db.query(Account).count()

        if existing == 0:

            alice = Account(
                owner="alice",
                balance=Decimal("5000.00")
            )

            bob = Account(
                owner="bob",
                balance=Decimal("1000.00")
            )

            db.add(alice)

            db.add(bob)

            db.commit()

    finally:

        db.close()


seed_accounts()


# ---------------------------------------------------
# Health route
# ---------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

 return templates.TemplateResponse(
    request=request,
    name="dashboard.html",
    context={
        "request": request
    }
)


# ---------------------------------------------------
# Get account balances
# ---------------------------------------------------

@app.get("/api/accounts")
def get_accounts(
    db: Session = Depends(get_db)
):

    accounts = db.query(Account).all()

    return [
        {
            "owner": a.owner,
            "balance": str(a.balance)
        }
        for a in accounts
    ]


# ---------------------------------------------------
# Get latest transactions
# ---------------------------------------------------

@app.get("/api/transactions")
def get_transactions(
    db: Session = Depends(get_db)
):

    txs = (
        db.query(Transaction)
        .order_by(Transaction.id.desc())
        .limit(20)
        .all()
    )

    return [
        {
            "id": tx.id,
            "sender": tx.sender,
            "receiver": tx.receiver,
            "amount": str(tx.amount),
            "status": tx.status,
            "packet_hash": tx.packet_hash
        }
        for tx in txs
    ]


# ---------------------------------------------------
# Inject encrypted packet into mesh
# ---------------------------------------------------

@app.post("/api/demo/send")
def send_demo_payment():

    packet = demo_service.create_packet(
        sender="alice",
        receiver="bob",
        amount=Decimal("500.00"),
        pin_hash="demo-pin"
    )

    mesh.inject_packet(
        "phone-alice",
        packet
    )

    return {
        "message": "Packet injected into mesh",
        "packet_id": packet.packet_id
    }


# ---------------------------------------------------
# Run one gossip round
# ---------------------------------------------------

@app.post("/api/mesh/gossip")
def run_gossip():

    mesh.gossip_round()

    return {
        "message": "Gossip round completed"
    }


# ---------------------------------------------------
# Flush bridge uploads
# ---------------------------------------------------

@app.post("/api/mesh/flush")
def flush_mesh(
    db: Session = Depends(get_db)
):

    settlement_service = SettlementService(
        db
    )

    ingestion_service = BridgeIngestionService(
        settlement_service,
        idempotency_service
    )

    results = mesh.flush_bridges(
        ingestion_service.ingest
    )

    return results


# ---------------------------------------------------
# Inspect mesh state
# ---------------------------------------------------

@app.get("/api/mesh/state")
def mesh_state():

    state = {}

    for device_id, device in mesh.devices.items():

        state[device_id] = {
            "has_internet": device.has_internet,
            "packet_count": len(device.packets),
            "packets": [
                {
                    "packet_id": p.packet_id,
                    "ttl": p.ttl
                }
                for p in device.packets
            ]
        }

    return state


# ---------------------------------------------------
# Reset mesh + idempotency cache
# ---------------------------------------------------

@app.post("/api/mesh/reset")
def reset_mesh():

    for device in mesh.devices.values():

        device.packets.clear()

    idempotency_service.seen.clear()

    return {
        "message": "Mesh reset complete"
    }