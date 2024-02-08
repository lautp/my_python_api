from fastapi import Request
from fastapi.security import HTTPBearer
from utils.jwt_manager import get_current_user


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        try:
            print("<<<<<<<<<<<<<<execute>>>>>>>>>>>>>>>>")
            auth = await super().__call__(request)
            await get_current_user(auth.credentials)
        except Exception as e:
            print(str(e))