import base64
import time
import bcrypt
from fastapi_mail import ConnectionConfig
from settings import AuthSettings, get_settings, MailSettings
from cryptography.fernet import Fernet, InvalidToken
from binascii import Error as BinasciiError

def hash_password(password: str) -> str:
    pw = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt).decode("utf-8")


settings: AuthSettings = get_settings(AuthSettings)
cipher = Fernet(settings.secret_key.encode())


mail_settings: MailSettings = get_settings(MailSettings)
conf = ConnectionConfig(
    MAIL_USERNAME = mail_settings.username,
    MAIL_PASSWORD = mail_settings.password,
    MAIL_FROM = mail_settings.from_mail,
    MAIL_PORT = mail_settings.port,
    MAIL_SERVER = mail_settings.server,
    MAIL_FROM_NAME = mail_settings.from_name,
    # If port = 465 => MAIL_STARTTLS = False, MAIL_SSL_TLS = True
    # If port = 578 => MAIL_STARTTLS = True, MAIL_SSL_TLS = False
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

def generate_recovery_token(user_id: str) -> str:
    expiration_time = time.time() + 36000
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
        