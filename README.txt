SECUREVAULT — Zero‑Knowledge Style Encryption Vault
===============================================

SecureVault is a Flask web app that encrypts user files and protects the encryption key using a split‑key + carrier strategy.
The goal is to minimize trust in any single storage location and keep plaintext out of server persistence.

Core ideas (high level)
----------------------
- Payload encryption: AES‑256‑GCM (confidentiality + integrity).
- Key splitting: master key is split into 5 shards with a 3‑of‑5 reconstruction threshold.
- Carrier encoding: shards are embedded into PNG carrier images (steganography layer).
- Multi‑node dispersal: carrier images are distributed across isolated “nodes” (abstracted in UI as NODE‑A / NODE‑B / NODE‑C).

What you get
------------
- Encrypt page: upload one or more files → receive a ZIP of .enc vault artifacts.
- Decrypt page: upload the original .enc artifacts → receive a ZIP of restored files.
- Profile + History: view basic user stats and activity logs (no sensitive provider names exposed in UI).

Security notes (important)
-------------------------
- The server does NOT keep your plaintext files.
- Do NOT rename the downloaded .enc artifacts. They contain identifiers used for recovery.
- Ownership enforcement:
  - Decrypt rejects artifacts not owned by the current session user (server-side).
  - Decrypt also verifies vault ownership using the local DB history (Encrypt record) before attempting recovery.

Local setup
-----------
Requirements:
- Python 3.10+ recommended
- A working Google Drive API client (if using the Drive node)
- A working Dropbox app/token (if using the Dropbox node)

1) Create and activate a virtual environment:

   python -m venv .venv
   .\.venv\Scripts\activate

2) Install dependencies:

   pip install -r requirements.txt

3) Provide carrier images:

   Put at least 5 PNG images inside:
   photos/

   These are used as carriers for the embedded key shards.

4) Configure cloud credentials (do not commit these)
---------------------------------------------------
The project uses local credential files. These MUST stay local:
- client_secret.json   (Google API client secret)
- token.json           (generated Google token)
- dropbox_secrets.json (Dropbox refresh token / secrets)

They are ignored by git via .gitignore.

Run the web app
--------------
Start:

   python app.py

Then open:
   http://127.0.0.1:5000/

Project structure (simplified)
------------------------------
- app.py                 Flask routes (auth, encrypt, decrypt, profile, history)
- core/                  crypto + encoding/decoding helpers
- templates/             HTML pages
- static/                CSS/JS (UI + transitions)
- photos/                carrier PNGs (local only)
- storage_1/ storage_2/ storage_3/   local node caches (gitignored)

GitHub / pushing code
---------------------
Before pushing, confirm secrets are not staged:

   git status

Never commit:
- client_secret.json
- token.json
- dropbox_secrets.json
- database.db

License
-------
Educational project.

