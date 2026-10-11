import jwt
from fastapi import HTTPException


class PyJWTTokenService:
    def __init__(self,private_key:str,public_key:str|None,algorithm:str):
        self._private_key = private_key
        self._public_key = public_key
        self._algorithm = algorithm

    def encode(self, payload: dict) -> str:
        return jwt.encode(payload, self._private_key, algorithm=self._algorithm)

    def decode(self, token: str) -> dict:
        try:
            return jwt.decode(token,self._private_key if not self._public_key else self._public_key, algorithms=[self._algorithm])
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid token")