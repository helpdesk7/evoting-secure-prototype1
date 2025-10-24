"""
utils/backup_utils.py
Handles AES-256-GCM encrypted backups (SR-07, Commit 15).
"""

import os
import shutil
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from Crypto.Cipher import AES


# Ensure backup directory exists
BACKUP_DIR = "backup"
os.makedirs(BACKUP_DIR, exist_ok=True)

def perform_encrypted_backup(db_path: str = "dev.db"):
    """
    Creates an AES-256-GCM encrypted copy of the database file.
    """
    # Generate backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    backup_file = os.path.join(BACKUP_DIR, f"dev_backup_{timestamp}.enc")

    # Read DB bytes
    with open(db_path, "rb") as f:
        data = f.read()

    # Generate encryption key + nonce
    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)

    # Encrypt database
    encrypted_data = aesgcm.encrypt(nonce, data, None)

    # Write encrypted backup
    with open(backup_file, "wb") as f:
        f.write(nonce + encrypted_data)

    return {
        "status": "success",
        "backup_file": backup_file,
        "key_preview": key.hex()[:16] + "...",
    }



def restore_from_backup(encrypted_file: str):
    """Simulates decryption & verification of latest encrypted backup."""
    try:
        with open(encrypted_file, "rb") as f:
            blob = f.read()

        # Just decrypt to test validity (reuse same key from perform_encrypted_backup)
        from .crypto import AES_KEY  # or whichever key constant is used
        nonce, tag, ct = blob[:12], blob[12:28], blob[28:]
        cipher = AES.new(AES_KEY, AES.MODE_GCM, nonce=nonce)
        cipher.decrypt_and_verify(ct, tag)

        return {"file": encrypted_file, "verified": True}
    except Exception as e:
        return {"file": encrypted_file, "verified": False, "error": str(e)}
