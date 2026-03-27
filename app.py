import requests
from flask import Flask, request
from datetime import datetime
from threading import Thread
import time

# =========================
# CONFIG
# =========================
TOKEN = "8704948433:AAEmCjobJckYRnQUZ-cfVQT7VFFeSa9aAMA"
CHAT_ID = "-1002497463613"

TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

app = Flask(__name__)

active_trades = {}

# =========================
# SEND TELEGRAM MESSAGE
# =========================
def send_telegram(message):
    requests.post(TELEGRAM_URL, json={
        "chat_id": CHAT_ID,
        "text": message
    })


# =========================
# SEND VIP SIGNAL
# =========================
def send_signal(pair, direction, price, confidence):
    time_now = datetime.now().strftime("%I:%M:%S %p")

    message = f"""
🔥 MARVEL-CORE AI TRADING SIGNAL 🔥

📊 Pair: {pair}
📈 Direction: {direction}

💰 Entry: {price}

🎯 TP: +0.5% - 1%
🛑 SL: -0.5%

🔥 Confidence: {confidence}%
🕒 {time_now}

⚡ MARVEL AI Engine
"""

    send_telegram(message)

    trade_id = f"{pair}_{time_now}"

    active_trades[trade_id] = {
        "pair": pair,
        "entry": float(price),
        "direction": direction
    }

    Thread(target=check_result, args=(trade_id,)).start()


# =========================
# GET LIVE PRICE
# =========================
def get_price(pair):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={pair}"
        data = requests.get(url).json()
        return float(data["price"])
    except:
        return None


# =========================
# RESULT CHECKER
# =========================
def check_result(trade_id):
    time.sleep(60)

    trade = active_trades.get(trade_id)
    if not trade:
        return

    pair = trade["pair"]
    entry = trade["entry"]
    direction = trade["direction"]

    current_price = get_price(pair)

    if current_price is None:
        return

    if direction == "BUY":
        result = "WIN ✅" if current_price > entry else "LOSS ❌"
    else:
        result = "WIN ✅" if current_price < entry else "LOSS ❌"

    message = f"""
📊 TRADE RESULT

📊 {pair}
Entry: {entry}
Exit: {current_price}

Result: {result}
RISK MANAGEMENT: Use 5% of your Capital
"""

    send_telegram(message)

    with open("results.csv", "a") as f:
        f.write(f"{pair},{entry},{current_price},{result}\n")

    del active_trades[trade_id]


# =========================
# WEBHOOK RECEIVER
# =========================
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    pair = data.get("pair")
    direction = data.get("direction")
    price = data.get("price")
    confidence = data.get("confidence", 80)

    if pair and direction and price:
        send_signal(pair, direction, price, confidence)

    return {"status": "ok"}


# =========================
# START NGROK + SERVER
# =========================
def start_system():
    from pyngrok import ngrok

    public_url = ngrok.connect(5000)
    print("====================================")
    print("🔥 YOUR WEBHOOK URL:")
    print(f"{public_url}/webhook")
    print("====================================")

    app.run(host="0.0.0.0", port=5000)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    start_system()
