from pydantic import BaseModel, Field, field_validator
from typing import Optional


# --- 使用者與認證模型 ---
class User(BaseModel):
    """基本使用者資訊"""

    username: str
    role: str  # "doctor" 或 "researcher"


class UserInDB(User):
    """存放在資料庫中的使用者資訊 (含雜湊密碼)"""

    hashed_password: str


class Token(BaseModel):
    """OAuth2 回傳的 JWT 格式"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """從 JWT 中解析出來的資料"""

    username: Optional[str] = None
    role: Optional[str] = None


# --- 醫療資料模型 ---
class PatientRecord(BaseModel):
    """
    完整病歷模型 (醫生可見)
    展示第一道防線：嚴格的型別驗證與格式限制
    """

    # 限制 patient_id 必須是 PT-開頭加上6位數字 (例如: PT-123456)
    patient_id: str = Field(..., pattern=r"^PT-\d{6}$")
    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., ge=0, le=150)  # 年齡必須在 0-150 之間

    # 診斷結果限制長度，防止緩衝區溢出或惡意長字串攻擊
    diagnosis: str = Field(..., max_length=500)

    # 敏感資訊：身分證字號與詳細病史
    ssn: str = Field(..., pattern=r"^[A-Z]\d{9}$")  # 台灣身分證格式簡易驗證
    medical_history: str = Field(..., max_length=1000)

    @field_validator("name")
    @classmethod
    def name_must_not_contain_special_chars(cls, v: str) -> str:
        # 簡易驗證：名字不允許特殊符號 (展示自訂驗證邏輯)
        if any(char in v for char in "@#$%^&*<>"):
            raise ValueError("Name cannot contain special characters")
        return v


class PatientPublic(BaseModel):
    """
    去識別化病歷模型 (研究員可見)
    隱藏敏感欄位 (ssn, medical_history)，並將年齡模糊化
    """

    patient_id: str
    age_group: str  # 例如: "20-30", "30-40"
    diagnosis: str
