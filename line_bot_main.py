import os
import time
from dotenv import load_dotenv
load_dotenv()

from fastapi import Request, FastAPI, HTTPException
from linebot.models import TextSendMessage
from linebot import (
    WebhookParser,
    WebhookHandler

)
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
    
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)


from src.bot.message import send_message
from src.common.enum import SystemMessageEnum

LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', None)
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)


configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

app = FastAPI()
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(LINE_CHANNEL_SECRET)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.post("/callback")
async def handle_callback(request: Request):
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessageContent):
            continue

        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    main()
    message = event.message.text
    reply_message = "抱歉....目前不提供聊天服務"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))


def main():

    send_message(SystemMessageEnum.BEGIN_MESSAGE.value)
    c = 0
    while c < 5:
        send_message("交易成功 已經成交")
        c += 1
        time.sleep(10)
    
    send_message(SystemMessageEnum.END_MESSAGE.value)



if __name__ == "__main__":
    send_message("""幣安API 問題: \n 
                    Error Message: 3333""")
