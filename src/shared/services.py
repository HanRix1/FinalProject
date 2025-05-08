from uuid import UUID
from fastapi import HTTPException, Request


class AuthService:
    async def autorize_user(
        self, request: Request, user_id: UUID, role: str = None
    ) -> None:
        session_data = request.session
        if "user_id" in session_data:
            raise HTTPException(status_code=401, detail="User already autorize")

        session_data["user_id"] = str(user_id)
        # session_data["user_role"] = str(role)

    async def deautorize_user(self, request: Request, user_id: str) -> None:
        session_data = request.session
        if "user_id" in session_data:
            del session_data["user_id"]
            # del session_data["user_role"]
            # Место для логгера
        else:
            # Место для логгера
            raise HTTPException(
                status_code=400, detail=f"User {user_id} is not currently authorized."
            )

    async def check_autorization(self, request: Request) -> str:
        session_data = request.session
        if "user_id" not in session_data:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return session_data["user_id"]
