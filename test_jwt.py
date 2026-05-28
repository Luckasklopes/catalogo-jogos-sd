from app.core.config import settings
import jwt
print(repr(settings.JWT_PUBLIC_KEY_PEM))
try:
    public_key = settings.JWT_PUBLIC_KEY_PEM.replace('\\n', '\n')
    print("Public key repr:", repr(public_key))
    # We don't have a valid token, but we can see if loading the key fails.
    # PyJWT lazy loads the key when verifying signature.
    # Let's force it to load the key by importing cryptography
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    load_pem_public_key(public_key.encode('utf-8'))
    print("Key loaded successfully!")
except Exception as e:
    print(f"Exception: {type(e).__name__}: {e}")
