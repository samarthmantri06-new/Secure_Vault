# SecureVault — Zero‑Knowledge Style File Vault

SecureVault is a Flask-based web application for encrypting files and enabling recovery using a **split‑key, threshold reconstruction** approach. The system is designed so **no single storage location** is enough to recover the master key.

**Live deployment:** `https://pirateee.pythonanywhere.com/`

---

## Key Features

- **AES‑256‑GCM encryption** for confidentiality + integrity
- **5 key shards** generated with a **3‑of‑5 reconstruction threshold**
- Shards are embedded into PNG **carrier images** (steganography layer)
- Carriers are distributed across isolated storage “nodes” (**NODE‑A / NODE‑B / NODE‑C** in UI)
- **Ownership enforcement on decrypt**
  - Server rejects vault artifacts that do not belong to the logged‑in user
  - Server additionally checks vault ownership in the DB before attempting recovery

---

## How It Works (High Level)

1. **Encrypt**: Your file is encrypted with AES‑256‑GCM.
2. **Split**: The encryption key is split into 5 shards (threshold 3).
3. **Encode**: Shards are embedded into PNG carriers.
4. **Disperse**: Carriers are distributed across isolated nodes.
5. **Decrypt**: Upload the original `.enc` artifact(s); the server verifies ownership, reconstructs the key (3 shards), then decrypts in memory.

---

## Tech Stack

- **Backend:** Flask (Python)
- **Crypto:** `cryptography` (AESGCM)
- **Storage Nodes:** modular upload/download helpers (node abstraction in UI)
- **Frontend:** HTML templates + JS + cyberpunk UI theme

---

## Local Setup

### Requirements
- Python **3.10+**
- 5+ PNG images in `photos/` (used as shard carriers)

### Install

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
