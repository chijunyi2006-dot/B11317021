from fastapi import FastAPI, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()

# 假資料庫
fake_users_db = {
    "alice": {"username": "alice", "password": "secret123"}
}

# Token 設定
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# -------- Token 建立 -------- #

def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(username: str):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": username, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -------- Token 驗證 -------- #

def verify_token(token: str, refresh: bool = False):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type", "access")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        if refresh and token_type != "refresh":
            raise HTTPException(status_code=401, detail="Not a refresh token")

        return username

    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid or expired")


# -------- Login：回傳 Access + Refresh Token -------- #

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), response: Response = None):
    user = fake_users_db.get(form_data.username)

    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(user["username"])
    refresh_token = create_refresh_token(user["username"])

    # Refresh Token 存在 HttpOnly Cookie 中
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax"
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# -------- Protected (需要 Access Token) -------- #

@app.get("/protected")
def protected(token: Optional[str] = Depends(oauth2_scheme)):
    username = verify_token(token)
    return {"message": f"Hello, {username}! You are authenticated."}


# -------- Refresh：用 Refresh Token 換新 Access Token -------- #

@app.post("/refresh")
def refresh_token(refresh_token: Optional[str] = Cookie(None)):
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    username = verify_token(refresh_token, refresh=True)
    new_access = create_access_token(username)

    return {
        "access_token": new_access,
        "token_type": "bearer"
    }


# -------- Logout：清除 Refresh Token Cookie -------- #

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
