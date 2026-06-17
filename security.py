from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from models import TokenData, User
from mock_db import get_user_from_db

# --- 安全設定 ---
# 在真實環境中，SECRET_KEY 必須從環境變數讀取，絕不能寫死在程式碼中
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 認證流程，指向我們稍後會在 main.py 實作的 /token 端點
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證明文密碼與雜湊密碼是否相符"""
    # bcrypt 需要位元組格式
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def authenticate_user(username: str, password: str) -> User | None:
    """模擬登入驗證：確認帳號存在且密碼正確"""
    user = get_user_from_db(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    # 回傳不含密碼的 User 物件
    return User(username=user.username, role=user.role)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    產生 JWT
    data: 通常包含欲加密的使用者資訊 (如 sub: username, role: doctor)
    """
    to_encode = data.copy()
    # 設定 Token 過期時間
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # 編碼並回傳 JWT 字串
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    核心依賴注入函式：
    1. 從請求 Header 取出 Token
    2. 解析 JWT 並驗證有效性
    3. 從 DB 取出對應使用者
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解碼 JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception

    # 從資料庫確認使用者仍然存在 (防止已刪除用戶的舊 Token)
    user = get_user_from_db(username=token_data.username)
    if user is None:
        raise credentials_exception
    return User(username=user.username, role=user.role)


# --- RBAC (角色存取控制) 依賴注入 ---
async def get_current_doctor(current_user: User = Depends(get_current_user)) -> User:
    """僅允許醫生角色存取"""
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Doctors only",
        )
    return current_user


async def get_current_researcher(
    current_user: User = Depends(get_current_user),
) -> User:
    """僅允許研究員角色存取"""
    if current_user.role != "researcher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Researchers only",
        )
    return current_user
