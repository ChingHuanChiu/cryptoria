import os
from dotenv import load_dotenv
load_dotenv()

from linebot import LineBotApi
from linebot.models import TextSendMessage


LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
USER_ID = os.getenv('USER_ID', None)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)


def send_message(message: str) -> None:

    line_bot_api.push_message(USER_ID, TextSendMessage(text=message))




