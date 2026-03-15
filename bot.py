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

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

keep_alive()
# ----------------------------------------------

# --- DATI CONFIGURATI ---
# Il TOKEN di Telegram lo lasciamo qui per ora
TOKEN = '8570081459:AAFl_p5dmdptTM_56kKpA0x2t3AxROV-k7Jc'
CHAT_ID = '1470247172'

# Qui usiamo la chiave "nascosta" che hai messo su Render (Environment Variable)
GROQ_KEY = os.environ.get('GROQ_API_KEY')

FEEDS = [
    "https://finance.yahoo.com/news/rss",
    "https://www.investing.com/rss/news.rss",
    "https://www.cnbc.com/id/10000664/device/rss/rss.html"
]

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_KEY)
sent_links = set()

def ask_ai(title):
    prompt = f"""
    SYSTEM: Sei un Trader professionista di un Hedge Fund.
    INPUT: News: '{title}'
    TASK:
    1. Analizza se questa notizia è un evento ad ALTO IMPATTO (capace di muovere l'asset di ALMENO l'1%).
    2. Se è una notizia minore, rispondi SOLO con la parola 'SKIP'.
    3. Se è un evento major, dai un segnale: 🟢 BUY [TICKER] o 🔴 SELL [TICKER]
       - Analisi: [Spiegazione rapida in ITALIANO]
    """
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
    # Messaggio di conferma che arriva a te su Telegram
    bot.send_message(CHAT_ID, "✅ Sistema AI Online su Render. Monitoraggio news attivo.")
    
    while True:
        for url in FEEDS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]:
                    if entry.link not in sent_links:
                        analysis = ask_ai(entry.title)
                        if "SKIP" not in analysis.upper():
                            final_msg = f"⚠️ **HIGH IMPACT SIGNAL**\n\n📰 {entry.title}\n\n{analysis}"
                            bot.send_message(CHAT_ID, final_msg, parse_mode='Markdown')
                        sent_links.add(entry.link)
            except Exception as e:
                print(f"Errore feed: {e}")
        
        time.sleep(300) # Controlla ogni 5 minuti

if __name__ == "__main__":
    monitor()

                        sent_links.add(entry.link)
            except Exception as e:
                print(f"Errore: {e}")
        time.sleep(120)

if __name__ == "__main__":
    monitor()
