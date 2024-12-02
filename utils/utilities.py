
import aiofiles
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

from auth.jwt_auth import JWTAuth
from auth.paseto_auth import PasetoAuth
from config.settings import settings

async def get_auth_instance():
    if settings.auth_mode == 'jwt':
        return JWTAuth()

    elif settings.auth_mode == 'paseto':
        if not (settings.paseto_private_key and settings.paseto_public_key):
            async with aiofiles.open(".secure/private_key.pem", "rb") as private_file:
                private_key_data = await private_file.read()
                private_key = serialization.load_pem_private_key(
                    private_key_data,
                    password=None
                )
                settings.paseto_private_key = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )

            async with aiofiles.open(".secure/public_key.pem", "rb") as public_file:
                public_key_data = await public_file.read()
                public_key = serialization.load_pem_public_key(public_key_data)
                settings.paseto_public_key = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )

        return PasetoAuth()

