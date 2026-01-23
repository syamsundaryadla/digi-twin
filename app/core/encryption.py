from cryptography.fernet import Fernet

# Generate key (in real apps, store this securely)
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

def encrypt_text(text: str) -> bytes:
    return cipher.encrypt(text.encode())

def decrypt_text(token: bytes) -> str:
    return cipher.decrypt(token).decode()
