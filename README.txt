#  SecureVault — Zero-Knowledge File Vault

> A secure, Flask-based file storage system utilizing a threshold-based key reconstruction model to eliminate single points of failure. 

SecureVault ensures that no single component or storage location is sufficient to recover encrypted data. By combining advanced encryption, key fragmentation, steganography, and distributed storage, access to encrypted files is physically impossible without combining multiple independent components.

---

##  Key Features

* **AES-256-GCM Encryption:** Ensures both absolute confidentiality and integrity of your stored files.
* **Threshold Key Splitting (3-of-5):** The master encryption key is cryptographically divided into 5 separate shards. A minimum of exactly 3 shards is required for successful reconstruction.
* **Steganographic Embedding:** Adds a powerful layer of obfuscation by hiding the key shards inside standard PNG image carriers.
* **Distributed Storage Abstraction:** Shards are dispersed across isolated, logical storage nodes (`NODE-A`, `NODE-B`, `NODE-C`) to prevent localized compromise.
* **Ownership Validation:** Decryption is strictly restricted to the original user through enforced server-side ownership checks.

---

##  System Workflow

###  Encryption Phase
1. The target file is encrypted using **AES-256-GCM**.
2. The encryption key is split into **5 distinct shards**.
3. These shards are individually embedded into **PNG carriers**.
4. The carriers are distributed across isolated **logical nodes**.

###  Decryption Phase
1. The user submits the encrypted artifact(s).
2. The server successfully verifies **user ownership**.
3. A minimum of **3 shards** are extracted from the retrieved PNG carriers.
4. The encryption key is successfully **reconstructed in memory**.
5. The file is securely decrypted and delivered to the user.

---

##  Design Philosophy

SecureVault is built around a zero-trust, defense-in-depth architecture:
* **Elimination of Single-Point Key Exposure:** The complete key never rests in a single location.
* **Layered Security:** Combines robust mathematical encryption with physical fragmentation and visual obfuscation.
* **Controlled Access:** Cryptographic security backed by strict ownership enforcement.

---

##  Tech Stack

* **Backend:** Flask (Python)
* **Cryptography:** `cryptography` library (AES-GCM)
* **Frontend:** HTML, CSS, JavaScript
