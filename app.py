# 載入相關套件
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
from datetime import datetime
import json
import mysql.connector

# 讀取linebot和mysql連線資訊
secretFile = json.load(open('secretFile.txt', 'r'))

# 建立Flask
app = Flask(__name__)

# 讀取LineBot驗證資訊
line_bot_api = LineBotApi(secretFile['channelAccessToken'])
handler = WebhookHandler(secretFile['channelSecret'])

# linebot接收訊息
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value: 驗證訊息來源
    signature = request.headers['X-Line-Signature']

    # get request body as text: 讀取訊息內容
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# linebot處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # linebot回傳訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='收到您的訊息囉!'))

    # 將文字資訊紀錄至資料庫
    conn = mysql.connector.connect(
        host=secretFile['host'],  # 連線主機名稱
        user=secretFile['user'],  # 登入帳號
        password=secretFile['passwd'])  # 登入密碼
    cursor = conn.cursor()
    query = 'INSERT INTO linebot.msg (time, msg) VALUES (%s, %s)'
    value = (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event.message.text)
    cursor.execute(query, value)
    conn.commit()
    conn.close()


# linebot處理照片訊息
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    # 使用者傳送的照片
    message_content = line_bot_api.get_message_content(event.message.id)

    # 照片儲存名稱
    fileName = event.message.id + '.jpg'

    # 儲存照片
    with open('./image/' + fileName, 'wb')as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    # linebot回傳訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='收到您上傳的照片囉!'))

    # 將照片路徑資訊紀錄至資料庫
    conn = mysql.connector.connect(
        host=secretFile['host'],  # 連線主機名稱
        user=secretFile['user'],  # 登入帳號
        password=secretFile['passwd'])  # 登入密碼
    cursor = conn.cursor()
    query = 'INSERT INTO linebot.upload_fig (time, file_path) VALUES (%s, %s)'
    value = (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fileName)
    cursor.execute(query, value)
    conn.commit()
    conn.close()
    
# 開始運作Flask
if __name__ == "__main__":
    app.run(host='0.0.0.0')