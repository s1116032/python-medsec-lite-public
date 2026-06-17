import bcrypt
from models import UserInDB, PatientRecord


# --- 模擬使用者資料庫 ---
# 使用 bcrypt 原生函式雜湊密碼 (需將字串編碼為 bytes)
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


fake_users_db = {
    "doctor": {
        "username": "doctor",
        "role": "doctor",
        "hashed_password": hash_password("password"),
    },
    "researcher": {
        "username": "researcher",
        "role": "researcher",
        "hashed_password": hash_password("password"),
    },
}


def get_user_from_db(username: str) -> UserInDB | None:
    """模擬從資料庫查詢使用者"""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


# --- 模擬病歷資料庫 ---
fake_patients_db = {
    "PT-123456": PatientRecord(
        patient_id="PT-123456",
        name="王小明",
        age=35,
        diagnosis="高血壓",
        ssn="A123456789",
        medical_history="無重大手術紀錄，有長期抽菸史。",
    ),
    "PT-654321": PatientRecord(
        patient_id="PT-654321",
        name="陳大同",
        age=28,
        diagnosis="一般感冒",
        ssn="B987654321",
        medical_history="無特殊疾病史。",
    ),
}
