from flask import Flask, request
import os # เพิ่ม os เข้ามา
import json
import requests as requests_lib
import google.generativeai as genai

app = Flask(__name__)

Line_Access_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"API Key ของ Gemini ไม่ถูกต้องหรือไม่ได้ตั้งค่า: {e}")



is_ai_active = True


def get_gemini_response(user_message):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # ทำให้ Gemini ตอบกลับเป็นภาษาไทยเสมอ
        prompt = f"User message: '{user_message}'. Please respond conversationally in the Thai language."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"!!!!!!!!!!!!!!! เกิดข้อผิดพลาดในการเรียก Gemini: {e} !!!!!!!!!!!!!!!")
        return "ขออภัยค่ะ ตอนนี้ระบบ AI มีปัญหา โปรดลองใหม่อีกครั้ง"


def ReplyMessage(Reply_token, TextMessage, Line_Access_TOKEN):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'
    Authorization = 'Bearer {}'.format(Line_Access_TOKEN)
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': Authorization
    }
    data = {
        "replyToken": Reply_token,
        "messages": [{"type": "text", "text": TextMessage}]
    }
    data = json.dumps(data)
    requests_lib.post(LINE_API, headers=headers, data=data)


@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == "POST":
        req = request.json
        if 'events' in req:
            for event in req['events']:
                if event['type'] == 'message' and event['message']['type'] == 'text':
                    user_message = event['message']['text']
                    Reply_token = event['replyToken']
                    
                    # 2. ประกาศว่าจะมีการแก้ไขค่าของตัวแปร is_ai_active ที่อยู่ข้างนอกฟังก์ชัน
                    global is_ai_active

                    # 3. ตรวจสอบว่าเป็น "คำสั่งพิเศษ" หรือไม่
                    if user_message == "/เปิดai":
                        is_ai_active = True
                        ReplyMessage(Reply_token, "✅ ระบบ AI เปิดใช้งานแล้ว", Line_Access_TOKEN)
                    
                    elif user_message == "/ปิดai":
                        is_ai_active = False
                        ReplyMessage(Reply_token, "❌ ระบบ AI ปิดใช้งานแล้ว", Line_Access_TOKEN)

                    # 4. ถ้าไม่ใช่คำสั่ง และ AI กำลังเปิดใช้งานอยู่
                    elif is_ai_active:
                        # ส่งข้อความไปให้ AI ประมวลผลตามปกติ
                        response_message = get_gemini_response(user_message)
                        ReplyMessage(Reply_token, response_message, Line_Access_TOKEN)
                    
                    # ถ้า AI ปิดอยู่ และไม่ใช่คำสั่ง ก็จะไม่ทำอะไรเลย (บอทจะเงียบ)

        return "POST", 200
    elif request.method == "GET":
        return "GET", 200

