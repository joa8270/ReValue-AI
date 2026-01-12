from fastapi import APIRouter, Request, HTTPException, Header
from linebot.v3.webhook import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError

# 引入我們的新設定和新服務
from app.core.config import settings
from app.services.line_bot_service import LineBotService

router = APIRouter()

# 初始化服務 (這裡會連帶初始化 Wizard Agent)
line_bot_service = LineBotService()
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@router.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    """
    LINE Webhook 入口
    負責接收訊息，並轉交給 LineBotService 處理
    """
    if x_line_signature is None:
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature header")

    # 取得原始訊息
    body = await request.body()
    body_as_str = body.decode("utf-8")

    try:
        # 驗證簽章並解析事件
        events = parser.parse(body_as_str, x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 將每一個事件都交給 Service 的 handle_event 統一處理
    for event in events:
        await line_bot_service.handle_event(event)

    return "OK"