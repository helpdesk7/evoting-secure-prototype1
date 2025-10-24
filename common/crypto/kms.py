from __future__ import annotations
import os, binascii

class LocalKMS:
    """
    Very simple KMS facade that loads a 32-byte AES-256 key from env AES_MASTER_KEY (hex).
    Example:
      AES_MASTER_KEY=0123456789abcdef... (64 hex chars)
    """
    def __init__(self, env_var: str = "AES_MASTER_KEY"):
        self.env_var = env_var
        hex_key = os.getenv(env_var, "").strip()
        if not hex_key:
            raise RuntimeError(f"{env_var} is not set")
        try:
            self._key = binascii.unhexlify(hex_key)
        except binascii.Error as e:
            raise RuntimeError(f"{env_var} must be hex") from e
        if len(self._key) != 32:
            raise RuntimeError(f"{env_var} must be 32 bytes (64 hex chars), got {len(self._key)} bytes")

    def get_key(self) -> bytes:
        return self._key