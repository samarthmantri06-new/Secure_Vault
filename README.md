<div align="center">

# SecureVault

### Distributed-key encrypted file vault

A Flask file vault that uses **threshold key reconstruction** to eliminate single points of failure. No single component or storage location is sufficient to decrypt stored data on its own.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-backend-000000?logo=flask&logoColor=white)
![AES](https://img.shields.io/badge/AES--256--GCM-encryption-0f766e)
![Shamir](https://img.shields.io/badge/Shamir-3--of--5-8250df)
![Cloud](https://img.shields.io/badge/Nodes-Local%20%C2%B7%20Drive%20%C2%B7%20Dropbox-4285F4)

[Features](#key-features) · [Security model](#security-model) · [Tech stack](#tech-stack) · [Setup](#local-setup) · [Structure](#project-structure) · [Limitations](#known-limitations--future-work)

</div>

---

## Key features

| Feature | What it does |
|---|---|
| **AES-256-GCM encryption** | Ensures both confidentiality and integrity of your stored files. |
| **Threshold key splitting (3-of-5)** | The master encryption key is cryptographically divided into 5 separate shards. A minimum of exactly 3 shards is required for reconstruction. |
| **Steganographic carrier encoding** | Each key shard is invisibly embedded into a PNG carrier image, adding an additional obfuscation layer. |
| **Multi-node dispersal** | Carrier images are distributed across physically isolated storage locations (local nodes, Google Drive and Dropbox), referred to in the UI as NODE-A / NODE-B / NODE-C. |
| **Ownership-bound artifacts** | Every encrypted vault artifact contains encoded identifiers; decryption is blocked server-side for any session that does not own the corresponding vault record. |

### How it fits together

```
 file ──► AES-256-GCM ──► .enc artifact
              │
            key ──► Shamir 3-of-5 ──► 5 shards ──► hidden in 5 PNGs ──► local / Google Drive / Dropbox
                                                                              (any 3 rebuild the key, in memory only)
```

---

## Security model

SecureVault is a defence-in-depth design combining mathematical encryption with physical key dispersal.

| Layer | Role |
|---|---|
| **AES-256-GCM** | Robust mathematical security for file confidentiality and integrity. |
| **Threshold key splitting (3-of-5)** | The master key is divided into 5 shards; exactly 3 are needed to rebuild it. |
| **Layered security** | Combines encryption with physical fragmentation and visual obfuscation. |
| **Controlled access** | Cryptographic security backed by strict ownership enforcement. |

### What the server does and doesn't do

- ✅ Does **not** persist your plaintext files after the response is sent.
- ✅ Does **not** persist the reconstructed decryption key. The key is held in memory only for the duration of the encrypt/decrypt request.
- ✅ No single storage location holds enough information to recover a file on its own. Recovery requires **compromising a threshold of independent storage locations** (at least 3 of the 5 dispersed shard carriers).
- ⚠️ The key is generated and reconstructed **server-side**. The server sees the plaintext during encryption and the reconstructed key during decryption. **The guarantee is dispersal and threshold access, not client-side-only encryption.**
- ⚠️ Do **not** rename the downloaded `.enc` artifacts. They contain identifiers used for key recovery.

### Ownership enforcement (two levels)

1. **Filename check:** decrypt rejects artifacts whose filename does not match the current session user. *(UX guard: clearer error message; not the primary security boundary.)*
2. **Vault ownership check:** decrypt also verifies vault ownership via the local DB history (Encrypt record) before attempting key recovery. *(Defence-in-depth check.)*

The primary security guarantee is cryptographic: decryption is impossible without reconstructing the key from a threshold of shards.

---

## Tech stack

| Layer | Tools |
|---|---|
| **Backend** | Flask (Python) |
| **Cryptography** | `cryptography` library (AES-GCM), `shamir-mnemonic` or equivalent (key splitting) |
| **Frontend** | HTML, CSS, JavaScript |

---

## Local setup

**Requirements**

- Python 3.10+ recommended
- A working Google Drive API client (if using the Drive node)
- A working Dropbox app / token (if using the Dropbox node)

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\activate        # Windows
source .venv/bin/activate        # macOS / Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Provide carrier images

Put at least 5 PNG images inside the `photos/` directory. These are used as carriers for the embedded key shards.

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in the required value:

```bash
cp .env.example .env   # or copy manually on Windows
```

| Variable | Required | Description |
|---|---|---|
| `FLASK_SECRET_KEY` | **Yes** | Flask session signing key. Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_DEBUG` | No (default `false`) | Enables Werkzeug debugger for local dev only. **Never `true` in production.** |

Load the `.env` before starting (e.g. via python-dotenv or your shell):

```powershell
$env:FLASK_SECRET_KEY="<your_generated_key>"   # PowerShell
```

### 5. Configure cloud credentials (do not commit these)

The project uses local credential files. These **must** stay local and are listed in `.gitignore`:

| File | Purpose |
|---|---|
| `client_secret.json` | Google API client secret |
| `token.json` | Generated Google OAuth token |
| `dropbox_secrets.json` | Dropbox refresh token / secrets |

### 6. Run the web app

```bash
python app.py
```

Then open <http://127.0.0.1:5000/>.

---

## Project structure

```
app.py                  Flask routes (auth, encrypt, decrypt, profile, history)
core/                   Crypto + steganography helpers
templates/              HTML pages
static/                 CSS / JS (UI + transitions)
photos/                 Carrier PNGs (local only, gitignored)
storage_1/ _2/ _3/      Local node caches (gitignored)
.env.example            Environment variable template
```

---

## Known limitations / future work

These are known gaps scoped out of the current version intentionally, not oversights.

- [ ] **No CSRF protection yet.** Flask-WTF or a manual CSRF token check has not been added to the encrypt/decrypt POST routes.
- [ ] **No rate limiting on login/signup.** Brute-force protection (e.g. Flask-Limiter) is not implemented.
- [ ] **Session cookies not yet marked `Secure` / `SameSite`.** Should be configured before any public deployment (`app.config['SESSION_COOKIE_SECURE']`, `app.config['SESSION_COOKIE_SAMESITE']`).
- [ ] **Vault IDs are random 7-digit integers.** The space is large enough for personal use (with collision-retry now in place), but a UUID4 would be more robust at scale.

---

## Before pushing to GitHub

Confirm secrets are not staged:

```bash
git status
```

**Never commit:** `.env` · `client_secret.json` · `token.json` · `dropbox_secrets.json` · `database.db`

---

## License

Educational project.
