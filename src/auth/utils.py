from datetime import datetime, timezone
from cryptography.fernet import Fernet, InvalidToken
from binascii import Error as BinasciiError
from fastapi_mail import ConnectionConfig
import base64
import bcrypt

from shared.settings import AuthSettings, get_settings, MailSettings


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


settings: AuthSettings = get_settings(AuthSettings)
cipher = Fernet(settings.secret_key.encode())


mail_settings: MailSettings = get_settings(MailSettings)
conf = ConnectionConfig(
    MAIL_USERNAME=mail_settings.username,
    MAIL_PASSWORD=mail_settings.password,
    MAIL_FROM=mail_settings.from_mail,
    MAIL_PORT=mail_settings.port,
    MAIL_SERVER=mail_settings.server,
    MAIL_FROM_NAME=mail_settings.from_name,
    # If port = 465 => MAIL_STARTTLS = False, MAIL_SSL_TLS = True
    # If port = 578 => MAIL_STARTTLS = True, MAIL_SSL_TLS = False
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


def generate_recovery_token(user_id: str) -> str:
    expiration_time = datetime.now(timezone.utc).timestamp() + 36000
    data = f"{user_id}:{expiration_time}".encode()
    token = cipher.encrypt(data)
    return base64.urlsafe_b64encode(token).decode()


def decode_recovery_token(token: str):
    try:
        token = base64.urlsafe_b64decode(token.encode())
    except (BinasciiError, ValueError) as e:
        raise ValueError("Invalid base64 encoding") from e

    try:
        decrypted_data = cipher.decrypt(token).decode()
    except InvalidToken as e:
        raise ValueError("Invalid or expired recovery token") from e

    try:
        user_id, expiration_time = decrypted_data.split(":")
        return user_id, expiration_time
    except ValueError as e:
        raise ValueError("Malformed recovery token data") from e


async def is_overlap(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """
    Проверяет, пересекаются ли два временных интервала.
    Возвращает True, если есть пересечение.
    """
    return not (a_end <= b_start or a_start >= b_end)