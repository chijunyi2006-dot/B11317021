from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from google_oauth import verify_google_id_token, exchange_code_for_tokens
from auth_utils import create_access_token, get_current_user_email

app = FastAPI(title="資工系 114-Backend 示範專案")

# 定義前端傳入的資料格式
class TokenRequest(BaseModel):
    """[架構B]前端直接傳 id_token"""
    id_token: str


class CodRequest(BaseModel):
    """[架構A]前端直接傳 authorization code,後端負責換 token"""
    code: str
    redirect_uri: str







@app.post("/auth/google/code",summary="[架構A] 用 Code 換取 JWT")    
async def google_auth_with_code(request:CodRequest):







    tokens = exchange_code_for_tokens(request.code,request.redirect_uri)


    google_id_token = tokens.get("id_token")
    if not google_id_token:
        raise HTTPException(status_code=400,detail="Gllgle 未回傳 id_token")
    
    user_info = verify_google_id_token(google_id_token)


    user_email = user_info.get("email")
    if not user_email:
        raise HTTPException(status_code=400, detail="Google 帳號未提供 Email")
    

    access_token = create_access_token(data={"sub" : user_email})

    return{
        "access_token":access_token,
        "token_type": "bearer",
        "user":{
            "name":user_info.gey("name"),
            "email": user_email,
            "picture": user_info.get("picture")
        },
        #
        "google_access_token": tokens.get("access_token"),

    }






@app.post("/auth/google",summary="[架構B] 用ID Token 換取 JWT")
async def google_auth(request:TokenRequest):
    """
    
    """
    #
    user_info = verify_google_id_token(request.id_token)

    #
    user_email = user_info.get("email")
    if not user_email:
        raise HTTPException(status_code= 400 , detail="Google 帳號未提供 Email")
    




    access_token = create_access_token(data={"sub":user_email})

    return{
        "access_token":access_token,
        "token_type": "bearer",
        "user":{
            "name":user_info.gey("name"),
            "email": user_email,
            "picture": user_info.get("picture")
        },
    }



@app.get("/user/me",summary="取得當前使用者資訊")
async def read_users_me(current_user:str = Depends(get_current_user_email)):



    return{
        "msg": "成功通過 JWT 驗證",
        "user_email":current_user
    }
@app.get("/")
def    root():
    return{"message":"Hello FastAPI OAuth Demo"}