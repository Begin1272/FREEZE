# routes_ws/__init__.py

"""WebSocket 라우터 통합"""
from fastapi import APIRouter
from .esp32_ws import router as esp32_router
from .app_ws import router as app_router
from .audio_ws import router as audio_router
from .camera_ws import router as camera_router  # 💥 이 줄을 주석 처리합니다.

# 메인 라우터 생성
router = APIRouter(tags=["websocket"])

# 각 WebSocket 라우터 포함
router.include_router(esp32_router)
router.include_router(app_router)
router.include_router(audio_router)
router.include_router(camera_router)  # 💥 이 줄도 주석 처리합니다.

__all__ = ["router"]