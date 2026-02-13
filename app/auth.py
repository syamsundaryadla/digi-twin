import bcrypt

MAX_PASSWORD_LENGTH = 72


def hash_password(password: str) -> str:
    # bcrypt limit: max 72 bytes
    pwd_bytes = password.encode("utf-8")[:MAX_PASSWORD_LENGTH]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    pwd_bytes = password.encode("utf-8")[:MAX_PASSWORD_LENGTH]
    return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))
