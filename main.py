from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)
from datetime import datetime, timedelta

pause_users = {10}
# ✨ 你的 LINE Channel Access Token
CHANNEL_ACCESS_TOKEN = "7TUAxTlTZNptVns+JUWZA1+bcV5FUwsPHquDsc+IBEsDEi2UoWDhUpw6bJG+VcBBS+1xXtnhyCvqboCqYDj84y/UNtv13+aHFbt/bBQ8Kq+LJ5iHzR05KqhQM9kpCbOJYRX6HFv8jXpSC4WAx1J7bQdB04t89/1O/w1cDnyilFU="

AUTO_REPLY_ENABLED = True

@app.route("/", methods=["GET"])
def home():
    return "✅ LINE Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    print("✅ 收到 LINE 訊息：", body)

    try:
        event = body['events'][0]
        user_id = event['source']['userId']
        reply_token = event['replyToken']
        user_message = event['message']['text'].lower()

        # ✅ 暫停判斷：若使用者在暫停名單內且尚未過期，則略過回覆
        now = datetime.now()
        if user_id in pause_users and pause_users[user_id] > now:
            print(f"⏸️ 暫停自動回覆，直到 {pause_users[user_id]}")
            return "OK"

        # ✅ 若有特定字詞或情境認定是人工回覆（這部分依你怎麼偵測手動回覆來判斷）
        if user_message.startswith("人工已回覆") or user_message.startswith("#manual"):
            pause_users[user_id] = now + timedelta(minutes=3)
            print(f"⏸️ 使用者 {user_id} 被暫停自動回覆到 {pause_users[user_id]}")
            return "OK"


        # 🧑‍⚕️ 自動回覆邏輯
        if "視訊診療" in user_message or "居家檢測" in user_message or "居家" in user_message or "檢測" in user_message or "視訊診療三步驟" in user_message or "視訊診療適合對象" in user_message or "視訊看診提醒" in user_message or "批價領藥方式" in user_message or "什麼是居家睡眠檢測" in user_message or "居家睡眠檢測" in user_message or "居家睡眠" in user_message or "睡眠" in user_message or "什麼是居家心電圖檢測" in user_message or "居家心電圖檢測" in user_message or "居家心電圖" in user_message or "心電圖" in user_message or "心律不整" in user_message or "什麼是連續血糖監測" in user_message or "連續血糖監測" in user_message or "連續血糖" in user_message or "如何預約檢測" in user_message or "預約檢測" in user_message or "會員查詢" in user_message or "最新資訊" in user_message:
            reply_text = ""
        elif "早安" in user_message:
            reply_text = "早安，今天有安排什麼嗎？記得補充水分，維持好精神。"
        elif "累" in user_message:
            reply_text = "了解，可能需要多讓自己休息一下。有需要也別忘了適時放鬆。"
        elif "哈囉" in user_message or "你好" in user_message or "您好" in user_message or "哈嘍" in user_message or "HI" in user_message or "Hi" in user_message or "hello" in user_message or "Hello" in user_message or "HELLO" in user_message or "嗨" in user_message:
            reply_text = "您好，\n這裡是臺北醫學大學 遠距服務中心，有任何問題可點選下方圖文選單中的「視訊診療」、「居家檢測」獲得答案!"
        elif "感冒" in user_message or "不舒服" in user_message:
            reply_text = "注意保暖，適當補充水分與休息，如有症狀建議就醫評估。"
        elif "謝謝" in user_message:
            reply_text = "不客氣，保持穩定的生活作息會更有幫助🧡。"
        elif "睡不著" in user_message or "失眠" in user_message:
            reply_text = "難入睡的話，可以試著放鬆一下心情，睡前別滑太久手機唷。"
        elif "頭痛" in user_message or "頭暈" in user_message:
            reply_text = "有頭痛或頭暈時，建議稍微休息，補充水分。如果持續不舒服，建議就醫檢查。"
        elif "壓力" in user_message or "焦慮" in user_message:
            reply_text = "當壓力大時，先深呼吸幾次也許有幫助，有時讓自己放鬆一下反而能更有力量。"
        elif "吃什麼" in user_message or "午餐" in user_message or "晚餐" in user_message:
            reply_text = "如果還沒吃飯，建議來點均衡的餐點，簡單但營養，對身體會比較舒服唷。"
        elif "喝水" in user_message:
            reply_text = "水分很重要，今天也記得多補充水唷～身體會感謝您的。"
        elif "心情不好" in user_message or "難過" in user_message or "想哭" in user_message:
            reply_text = "情緒低落的時候，不要勉強自己，給自己一點空間，有需要也可以找人聊聊。"
        else:
            reply_text = "有任何問題可點選下方圖文選單中的「視訊診療」、「居家檢測」獲得答案!\n其他問題請致電02-21765226或由圖文選單點選「專線電話」致電24小時專線電話，並請留下您的大名及連絡電話，謝謝您😊"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
        }

        # 拆成兩則訊息，一則問候，一則提示專人回覆
        data = {
            "replyToken":
            reply_token,
            "messages": [{
                "type": "text",
                "text": reply_text
            }, {
                "type": "text",
                "text": "以上為訊息自動回應\n緊急訊息稍後將由專人回覆，請稍等😊"
            }]
        }

        print("🔁 準備發送訊息給 LINE API...")
        response = requests.post("https://api.line.me/v2/bot/message/reply",
                                 headers=headers,
                                 data=json.dumps(data).encode('utf-8'))

        print("✅ 成功送出訊息，狀態碼：", response.status_code)
        print("📨 LINE 回應：", response.text)

    except Exception as e:
        print("⚠️ 發生錯誤：", e)

    return "OK"


app.run(host="0.0.0.0", port=3000)
