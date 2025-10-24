from secrets import token_bytes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def aes_gcm_encrypt(plaintext: bytes, kms, aad: bytes | None = None) -> tuple[bytes, bytes]:
    """
    Encrypt arbitrary bytes with AES-256-GCM using key from KMS.
    Returns (ciphertext_with_tag, nonce).
    """
    key = kms.get_key()
    aesgcm = AESGCM(key)
    nonce = token_bytes(12)
    ct = aesgcm.encrypt(nonce, plaintext, associated_data=aad)
    return ct, nonce