import os
import telebot
import feedparser
import time
import requests
from flask import Flask
import threading
from groq import Groq

# --- SISTEMA PER RENDERE IL BOT SEMPRE ATTIVO ---
app = Flask('')

@app.route('/')
def home():
    return "Il bot è vivo!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# --- DATI CONFIGURATI ---
TOKEN = '8570081459:AAFl_p5dmdptTM_56kKpA0x2t3AxROV-k7Jc'
CHAT_ID = '1470247172'
GROQ_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_KEY)
sent_links = set()

FEEDS = [
    "https://finance.yahoo.com/news/rss",
    "https://www.investing.com/rss/news.rss",
    "https://www.cnbc.com/id/10000664/device/rss/rss.html"
]

def ask_ai(title):
    prompt = f"Analizza se questa notizia finanziaria è ad alto impatto (muove il mercato >1%): '{title}'. Se no, scrivi solo SKIP. Se sì, scrivi: 🟢 BUY o 🔴 SELL [TICKER] + Analisi rapida in italiano."
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.1
        )
        return completion.choices[0].message.content
    except:
        return "SKIP"

def monitor():
    print("🚀 Bot avviato su Render!")
    try:
        bot.send_message(CHAT_ID, "✅ Sistema AI Online su Render. Monitoraggio news attivo.")
    except Exception as e:
        print(f"Errore Telegram: {e}")
    
    while True:
        for url in FEEDS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]:
                    if entry.link not in sent_links:
                        analysis = ask_ai(entry.title)
                        if "SKIP" not in analysis.upper():
                            msg = f"⚠️ **HIGH IMPACT SIGNAL**\n\n📰 {entry.title}\n\n{analysis}"
                            bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
                        sent_links.add(entry.link)
            except:
                pass
        time.sleep(300)

if __name__ == "__main__":
    # Avviamo Flask in un thread separato
    threading.Thread(target=run_flask).start()
    # Avviamo il monitoraggio nel thread principale
    monitor()
