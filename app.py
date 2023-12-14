from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import TextMessage, MessageEvent, TextSendMessage

app = Flask(__name__)

# 请替换为您的Channel Access Token和Channel Secret
line_bot_api = LineBotApi('CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('CHANNEL_SECRET')

def process_message(text):
    # 添加自定义条件，当用户输入"123"时，返回"321"
    if text == "123":
        return "321"
    else:
        # 在这里可以添加其他处理逻辑，例如调用GPT-3等
        return "机器人：我听不懂你在说什么！"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    reply_message = process_message(user_message)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))

if __name__ == "__main__":
    # 运行Flask应用程序
    app.run()
