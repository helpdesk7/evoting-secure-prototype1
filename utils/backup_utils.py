"""
utils/backup_utils.py
Handles AES-256-GCM encrypted backups (SR-07, Commit 15).
"""

import os
import shutil
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

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
