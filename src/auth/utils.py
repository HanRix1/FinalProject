import time
from uuid import UUID
import jwt
from settings import AuthSettings, get_settings


settings: AuthSettings = get_settings(AuthSettings)

def token_response(token: str):
    return {"access_token": token}


def sign_jwt(user_id: UUID) -> dict[str, str]:
    payload = {
        "user_id": user_id.hex, 
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, settings.secret, algorithm=settings.algorithm)

    return token_response(token)


def decode_jwt(token: str) -> dict[str, str]:
    try:
        decoded_token = jwt.decode(
            token, settings.secret, algorithms=[settings.algorithm]
        )
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}