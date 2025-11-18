""" 앱 클라이언트 WebSocket 핸들러 (topic 구독) """
import asyncio
import json
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from .utils import maybe_set_base_url_from_ws, log_exc, app_add, app_remove

router = APIRouter()

@router.websocket("/ws/app")
async def ws_app(websocket: WebSocket):
    """
    앱 클라이언트 연결 관리 (topic 기반 구독)
    - 클라이언트는 {"action":"subscribe", "topic":"..."} JSON 메시지로 구독
    """
    
    # 이 클라이언트가 구독한 토픽들을 저장하는 Set
    subscribed_topics = set()

    try:
        await websocket.accept()
        print(f"📱 앱 연결됨 (구독 대기 중...)")
    except Exception as e:
        log_exc("[APP accept]", e)
        return

    maybe_set_base_url_from_ws(websocket)
    
    try:
        while True:
            try:
                # 클라이언트의 메시지를 계속 기다림
                data = await websocket.receive_text()
                
                # 수신한 텍스트를 JSON으로 파싱
                msg = json.loads(data)
                action = msg.get("action")
                topic = msg.get("topic")

                # 구독 요청 처리
                if action == "subscribe" and topic:
                    await app_add(topic, websocket)     # 브로드캐스트 목록에 추가
                    subscribed_topics.add(topic)      # 이 연결이 끊길 때를 대비해 저장
                    print(f"📱 앱 구독: topic={topic} (현재 {len(subscribed_topics)}개 구독 중)")
                
                # (참고: 나중에 unsubscribe 로직도 여기에 추가할 수 있음)

            except json.JSONDecodeError:
                print(f"[APP] 경고: 잘못된 JSON 수신: {data}")
            except WebSocketDisconnect:
                break  # 클라이언트가 연결을 끊으면 while 루프 탈출
            except Exception as e:
                log_exc("[APP recv/process]", e)
                # 오류 발생 시에도 일단 계속 수신 시도
                
    finally:
        try:
            print(f"📱 앱 연결 끊김: {len(subscribed_topics)}개 토픽 정리 중...")
            # 이 클라이언트가 구독했던 모든 토픽에서 제거
            for topic in subscribed_topics:
                await app_remove(topic, websocket)
            
            await websocket.close()
        except Exception:
            pass  # 정리 중 오류는 무시
        
        print(f"📱 앱 연결 완전 종료.")