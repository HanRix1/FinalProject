import asyncio
from uuid import UUID
import bcrypt
from fastapi import HTTPException, Request, Security,status
from fastapi.security import APIKeyCookie
from auth.repository import UserRepository
from auth.schemas import UserLoginSchema, UserSchema, UserUpdateSchema
from auth.utils import hash_password


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    async def register_user(self, new_user: UserSchema) -> UUID:
        user = await self.user_repo.get_user_by_email(email=new_user.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        hashed_password = await asyncio.to_thread(hash_password, new_user.password)
        new_user_id = await self.user_repo.create_new_user(user=new_user, hashed_password=hashed_password)
        return new_user_id 
    
    async def verify_user(self, user: UserLoginSchema) -> UUID:
        db_user = await self.user_repo.get_user_by_email(email=user.email)

        if not db_user or not await asyncio.to_thread(
            bcrypt.checkpw,
            user.password.encode("utf-8"),
            db_user.password.encode("utf-8")
        ):
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )     
        return db_user.id
 
    async def remove_user(self, user_id) -> UUID:
        db_user = await self.user_repo.get_user_by_id(user_id=user_id)

        if not db_user:
            raise HTTPException(
                status_code=410,
                detail="User has been deleted"
            )
        deleted_user_id = await self.user_repo.delete_user_by_id(user_id=db_user.id)

        return deleted_user_id
    
    async def modernize_user(self, user_id: UUID, user_data: UserUpdateSchema):
        db_user = await self.user_repo.get_user_by_id(user_id=user_id)

        if not db_user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        updated_user = await self.user_repo.update_user_data(user_data=user_data, user_id=user_id)
        
        return updated_user
        

session_cookie = APIKeyCookie(name="session_id", auto_error=True)

class AuthService:
    async def get_current_user(self, request: Request, session: str = Security(session_cookie)) -> str:
        session_data = request.session
        if "user_id" not in session_data:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return session_data["user_id"]