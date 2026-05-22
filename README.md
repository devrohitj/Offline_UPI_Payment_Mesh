# UPI Offline Mesh — FastAPI Edition

> Offline UPI-style payment routing through a Bluetooth mesh network using FastAPI, RSA-OAEP, AES-256-GCM, SQLAlchemy, and distributed idempotency concepts.

---

## Overview

This project demonstrates how digital payments can propagate across nearby devices even when there is **zero internet connectivity**.

Imagine:
- you're inside a basement,
- there’s no cellular network,
- no Wi-Fi,
- no internet.

A sender creates an encrypted payment packet which travels device-to-device across a simulated Bluetooth mesh network until one bridge node regains internet access and uploads it to the backend for settlement.

The project focuses on solving **real distributed systems problems** found in payment infrastructure.

---

# Key Features

- Offline mesh payment propagation
- RSA-OAEP + AES-256-GCM hybrid encryption
- Tamper-proof transaction packets
- Exactly-once settlement semantics
- Replay attack prevention
- Thread-safe idempotency
- FastAPI backend architecture
- SQLAlchemy ORM integration
- Interactive dashboard UI
- Mesh network simulator

---

# Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite |
| Encryption | RSA-OAEP + AES-256-GCM |
| Frontend | Jinja2 + Vanilla JavaScript |
| Concurrency | Thread-safe services |
| Hashing | SHA-256 |
| Mesh Simulation | Python |

---

# System Architecture

```text
Sender Device (Offline)
        │
        ▼
Encrypt Payment Packet
(RSA + AES-GCM)
        │
        ▼
Bluetooth Mesh Propagation
        │
        ▼
Bridge Device Gets Internet
        │
        ▼
POST /api/bridge/ingest
        │
        ▼
FastAPI Backend
        │
        ├── SHA256(ciphertext)
        ├── Idempotency Claim
        ├── Decrypt Packet
        ├── Freshness Validation
        └── Transaction Settlement
```

---

# Core Engineering Challenges Solved

## 1. Secure Routing Through Untrusted Devices

### Problem

Payment packets travel through stranger devices in the mesh.

How do we prevent intermediaries from:
- reading transaction details,
- modifying amounts,
- tampering with receivers?

### Solution

Implemented hybrid encryption using:

- RSA-OAEP
- AES-256-GCM

Flow:
1. Generate AES session key
2. Encrypt payment JSON using AES-GCM
3. Encrypt AES key using server RSA public key
4. Transmit encrypted blob through mesh

AES-GCM provides authenticated encryption, meaning any ciphertext tampering immediately fails authentication during decryption.

---

## 2. Exactly-Once Settlement During Duplicate Storms

### Problem

Multiple bridge devices may upload the same payment packet simultaneously.

Without protection:
- duplicate debits occur,
- ledger corruption happens,
- settlement becomes inconsistent.

### Solution

Implemented atomic idempotency using:

```text
SHA-256(ciphertext)
```

Each incoming packet:
1. hashes ciphertext,
2. attempts atomic claim,
3. only first claimer proceeds,
4. duplicates are dropped immediately.

This simulates production-grade patterns such as:

```text
Redis SETNX
```

and exactly-once settlement guarantees used in fintech systems.

---

## 3. Replay Attack Prevention

### Problem

An attacker may capture a valid encrypted payment and replay it later.

### Solution

Implemented:
- signed timestamp validation,
- nonce-based uniqueness,
- replay hash detection.

Packets older than the allowed time window are rejected before touching the ledger.

Each transaction contains a unique nonce ensuring:
- legitimate repeated payments succeed,
- replayed packets are detected and dropped.

---

# API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Dashboard UI |
| GET | `/api/accounts` | Account balances |
| GET | `/api/transactions` | Transaction ledger |
| GET | `/api/mesh/state` | Mesh topology |
| POST | `/api/demo/send` | Inject payment into mesh |
| POST | `/api/mesh/gossip` | Run gossip round |
| POST | `/api/mesh/flush` | Upload bridge packets |
| POST | `/api/mesh/reset` | Reset mesh |

---

# Project Structure

```text
upi-offline-mesh/
│
├── main.py
├── models.py
├── crypto.py
├── mesh.py
├── demo.py
├── settlement.py
├── ingestion.py
├── idempotency.py
│
├── templates/
│   └── dashboard.html
│
└── static/
```

---

# Production-Level Concepts Demonstrated

- Distributed systems design
- Offline-first architecture
- Exactly-once processing
- Authenticated encryption
- Replay protection
- Concurrent transaction handling
- Transaction-safe settlement
- Service-oriented backend architecture

---


---
