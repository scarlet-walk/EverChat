from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
import socket

app = Flask(__name__)

# إنشاء عميل OpenAI باستخدام المفتاح من Secrets
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

@app.route('/chat')
def chat():
    return render_template('index.html')

@app.route('/get', methods=['POST'])
def get_bot_response():
    try:
        user_message = request.json.get("msg", "").strip()
        if not user_message:
            return jsonify({"reply": "⚠️ الرجاء كتابة رسالة قبل الإرسال."})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مساعد ذكي ودود."},
                {"role": "user", "content": user_message}
            ]
        )

        bot_reply = response.choices[0].message.content.strip()
        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"reply": f"❌ حدث خطأ في الخادم: {str(e)}"})

@app.route('/')
def home():
    return "✅ EverChat API يعمل! افتح /chat لتجربة البوت."

if __name__ == '__main__':
    # اختيار منفذ متاح تلقائيًا
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()

    print(f"🚀 Running on dynamic port: {port}")
    app.run(host='0.0.0.0', port=port)
