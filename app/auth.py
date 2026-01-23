from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

MAX_PASSWORD_LENGTH = 72


def hash_password(password: str) -> str:
    # bcrypt limit protection
    password = password[:MAX_PASSWORD_LENGTH]
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    password = password[:MAX_PASSWORD_LENGTH]
    return pwd_context.verify(password, hashed)
