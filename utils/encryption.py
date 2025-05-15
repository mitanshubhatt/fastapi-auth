from cryptography.fernet import Fernet, InvalidToken
from config.settings import settings
from utils.custom_logger import logger


class DataEncryptor:
    """
    A class to handle symmetric encryption and decryption of data using Fernet.
    """
    _fernet_instance: Fernet = None

    def __init__(self, encryption_key: str):
        """
        Initializes the DataEncryptor with a Fernet key.

        Args:
            encryption_key: The Fernet encryption key (URL-safe base64-encoded 32-byte key).

        Raises:
            ValueError: If the encryption_key is not provided or is invalid.
        """
        if not encryption_key:
            logger.error("Encryption key is not provided.")
            raise ValueError("Encryption key must be provided.")

        try:
            key_bytes = encryption_key.encode()  # Ensure the key is bytes
            self._fernet_instance = Fernet(key_bytes)
            logger.info("DataEncryptor initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Fernet with the provided key: {e}")
            raise ValueError(f"Invalid encryption key format or value: {e}")

    async def encrypt(self, plain_text: str) -> str:
        """
        Encrypts a string.

        Args:
            plain_text: The string to encrypt.

        Returns:
            The encrypted string (URL-safe base64 encoded).
            Returns the original text if it's empty or None.
        """
        if not plain_text:
            return plain_text
        try:
            encrypted_bytes = self._fernet_instance.encrypt(plain_text.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise ValueError(f"Encryption failed: {e}")

    async def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypts an encrypted string.

        Args:
            encrypted_text: The encrypted string (URL-safe base64 encoded).

        Returns:
            The decrypted string.
            Returns the original text if it's empty or None.

        Raises:
            ValueError: If decryption fails due to an invalid token or other errors.
        """
        if not encrypted_text:
            return encrypted_text
        try:
            decrypted_bytes = self._fernet_instance.decrypt(encrypted_text.encode())
            return decrypted_bytes.decode()
        except InvalidToken:
            logger.error("Decryption failed: Invalid token or key.")
            raise ValueError("Decryption failed: Invalid token or key.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during decryption: {e}")
            raise ValueError(f"Decryption failed: {e}")

