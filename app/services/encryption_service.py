import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Generate or load encryption key
def get_encryption_key():
    """Get or generate encryption key"""
    key_file = ".encryption_key"
    
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            key = f.read()
    else:
        # Generate new key
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        # Make file readable only by owner (Unix)
        try:
            os.chmod(key_file, 0o600)
        except:
            pass  # Windows doesn't support chmod, ignore
    
    return key

def encrypt_password(password: str) -> str:
    """Encrypt password"""
    if not password:
        return ""
    
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()

def decrypt_password(encrypted_password: str) -> str:
    """Decrypt password"""
    if not encrypted_password:
        return ""
    
    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_password.encode())
        return decrypted.decode()
    except Exception as e:
        # If decryption fails, return empty string
        return ""

