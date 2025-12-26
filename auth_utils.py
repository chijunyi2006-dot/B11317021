import os
from datetime import datetime, timedelta
from jose import jwt, JWSError
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY=os.getenv("SECRET_KEY","fallback-for-dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

#
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/google")

def create_access_token(data: dict):
    """建立 JWT Access Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_email(token: str = Depends(oauth2_scheme))->str:
    """
    解析 JWT並回傳使用者email
    - 用於受保護路由器的依賴注入
    - 自動從 Authorization:Bearer <token> 取得 token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "無法驗證憑證",
        headers= {"WWW-Authenticate": "Bearer"},
    )
    try:
        #
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        #
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWSError:
        raise credentials_exception
    
