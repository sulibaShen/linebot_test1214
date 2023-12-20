from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import *

from mongodb_function import *

import tempfile, os
import datetime
import time
import traceback

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

def process_message(text):
    msg = ''
    if text == "@讀取":
        datas = read_many_datas()
        datas_len = len(datas)
        msg = f'資料數量，一共{datas_len}條'
    elif text == '@查詢':
        datas = col_find('events')
        msg = str(datas)
    elif text == '@對話紀錄':
        datas = read_chat_records()
        print(type(datas))
        n = 0
        text_list = []
        for data in datas:
            if '@' in data:
                continue
            else:
                text_list.append(data)
            n+=1
        data_text = '\n'.join(text_list)
        msg = data_text[:5000]
    elif text == '@刪除':
        text = delete_all_data()
        msg = '已刪除成功'
    else:
        # 在这里可以添加其他处理逻辑，例如调用GPT-3等
        msg = str('openAI目前尚未導入，目前以模仿代替\n您說的話是不是\n' + text)
    return msg

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    try:
        data = json.loads(body)
        write_one_data(data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    reply_message = process_message(user_message)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))

@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
