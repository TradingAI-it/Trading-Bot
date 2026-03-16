import os
import threading
import time
import telebot
from flask import Flask
from groq import Groq

# --- CONFIGURAZIONE NUOVO BOT ---
TOKEN = "8787147048:AAHoCmF1pUVArSTo0BPawJui08rSwBgeDBs"
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
bot = telebot.TeleBot(TOKEN)

# --- WEB SERVER PER RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "TradingAI-it Bot is Running"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- PROMPT PROFESSIONALE ---
SYSTEM_PROMPT = """
Sei l'Analista Senior di 'TradingAI-it'. Stile istituzionale e analitico.
Quando ricevi un asset, genera un segnale così:

🟢 **STRATEGIA: BUY / LONG** o 🔴 **STRATEGIA: SELL / SHORT**
━━━━━━━━━━━━━━━━━━━━
💰 **ASSET:** [NOME ASSET]
💵 **ENTRY ZONE:** [PREZZO ATTUALE]
🎯 **TARGET 1:** [+2.00% circa]
🎯 **TARGET 2:** [+5.50% circa]
🛑 **STOP LOSS:** [-3.20% circa]
━━━━━━━━━━━━━━━━━━━━
⚡ **LEVA CONSIGLIATA:** 10x / 20x (Cross)
📊 **ANALISI TECNICA:** [RSI, Supporti/Resistenze e Volumi]

⚠️ *Nota: Gestione del rischio al 1-2%. Non è un consiglio finanziario.*
🔗 **Canale Ufficiale:** https://t.me/TradingAI_it
"""

# --- COMANDO NEWS ---
@bot.message_handler(commands=['news'])
def send_news(message):
    try:
        feed = feedparser.parse("https://it.cointelegraph.com/rss")
        msg = "📰 **ULTIME NOTIZIE CRYPTO**\n\n"
        for entry in feed.entries[:3]:
            msg += f"🔹 {entry.title}\n🔗 [Leggi di più]({entry.link})\n\n"
        bot.send_message(message.chat.id, msg, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        bot.reply_to(message, "⚠️ Errore nel recupero delle news.")

# --- GESTIONE MESSAGGI ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.2
        )
        risposta = completion.choices[0].message.content
        bot.reply_to(message, risposta, parse_mode="Markdown")
    except Exception as e:
        print(f"Errore: {e}")

# --- AVVIO ---
if __name__ == "__main__":
    # 1. Pulizia webhook
    bot.remove_webhook()
    
    # 2. Avvio Flask in un THREAD separato (così non blocca il bot)
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    
    print("Sistema operativo. Sto ascoltando i messaggi...")
    
    # 3. Avvio Polling (QUESTO deve essere l'ultimo comando)
    bot.infinity_polling(skip_pending=True)



