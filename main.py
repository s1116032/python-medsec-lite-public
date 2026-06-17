import asyncio
from datetime import timedelta
from typing import Union

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from models import Token, PatientRecord, PatientPublic, User
from security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_doctor,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from mock_db import fake_patients_db

# --- App 初始化 ---
app = FastAPI(
    title="MedSec-Lite",
    description="醫療級安全微服務 POC - 展示 FastAPI 的資安驗證、RBAC 與非同步 AI 整合",
    version="1.0.0",
)

# --- API 端點 ---


@app.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    登入端點：獲取 JWT Token
    (在 Swagger UI 右上角點擊 🔒 按鈕，輸入帳密即可授權)
    """
    # 1. 驗證帳密
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 產生 JWT (將 username 與 role 放入 payload)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get(
    "/patients/{patient_id}",
    response_model=Union[PatientRecord, PatientPublic],
    tags=["Patients"],
)
async def get_patient_record(
    patient_id: str, current_user: User = Depends(get_current_user)
):
    """
    讀取病歷：
    - 醫生: 回傳完整病歷
    - 研究員: 回傳去識別化病歷
    """
    if patient_id not in fake_patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient = fake_patients_db[patient_id]

    # 根據角色決定回傳資料 (RBAC 資料級別控管)
    if current_user.role == "doctor":
        return patient  # 回傳完整 PatientRecord
    elif current_user.role == "researcher":
        # 回傳去識別化 PatientPublic
        age_group = f"{patient.age // 10 * 10}-{patient.age // 10 * 10 + 9}"
        return PatientPublic(
            patient_id=patient.patient_id,
            age_group=age_group,
            diagnosis=patient.diagnosis,
        )
    else:
        raise HTTPException(status_code=403, detail="Access forbidden")


@app.delete(
    "/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Patients"]
)
async def delete_patient_record(
    patient_id: str, current_user: User = Depends(get_current_doctor)
):
    """
    刪除病歷：
    - 僅限醫生 角色，研究員呼叫會直接返回 403 Forbidden。
    """
    if patient_id not in fake_patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")

    # 模擬刪除資料
    del fake_patients_db[patient_id]
    return  # 204 No Content


@app.post("/ai/predict", tags=["AI Inference"])
async def ai_predict(current_user: User = Depends(get_current_user)):
    """
    模擬地端 AI 推論：
    - 使用 async/await 配合 asyncio.sleep 模擬長時間運算。
    - 證明非同步架構下，此 API 不會阻塞其他 API 請求。
    """
    # 模擬 AI 模型推論耗時 1 秒
    await asyncio.sleep(1)

    return {
        "status": "success",
        "user": current_user.username,
        "prediction": "Positive (模擬結果)",
        "confidence": 0.92,
    }


# 啟動指令提示 (方便測試)
if __name__ == "__main__":
    import uvicorn

    print("啟動 MedSec-Lite 服務...")
    print("Swagger UI: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
