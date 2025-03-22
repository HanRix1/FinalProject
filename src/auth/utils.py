import time
from uuid import UUID
import bcrypt
import jwt
from settings import AuthSettings, get_settings


settings: AuthSettings = get_settings(AuthSettings)

def token_response(token: str):
    return {"access_token": token}


def sign_jwt(user_id: UUID) -> dict[str, str]:
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }

    payload = {
        "user_id": user_id.hex, 
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, key=settings.secret, algorithm=settings.algorithm, headers=headers)

    return token_response(token)


def decode_jwt(token: str) -> dict[str, str]:
    try:
        decoded_token = jwt.decode(
            token, key=settings.secret, algorithms=[settings.algorithm]
        )
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except jwt.exceptions.PyJWTError as e:
        # можно добавить лоиги
        return None
    
def hash_password(password: str) -> str:
    pw = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt).decode("utf-8")

