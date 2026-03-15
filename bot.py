import os
import telebot
from groq import Groq
from flask import Flask
from threading import Thread

# --- CONFIGURAZIONE CORE ---
# Il Token è quello che mi hai fornito tu
TOKEN = "8570081459:AAFl_p5dmdptTM_56kKpA0x2t3AxROVk7Jc"
# La chiave Groq viene letta dalle variabili di ambiente di Render per sicurezza
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
bot = telebot.TeleBot(TOKEN)

# --- WEB SERVER PER RENDER ---
# Serve a mantenere il servizio attivo sulla porta 8080 ed evitare il "Port scan timeout"
app = Flask('')

@app.route('/')
def home():
    return "TradingAI-it Bot is Running"

def run():
    # Render usa la porta 8080 di default o quella definita nelle variabili
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- PROMPT PROFESSIONALE ---
SYSTEM_PROMPT = """
Sei l'Analista Senior di 'TradingAI-it', un esperto in mercati finanziari e criptovalute.
Il tuo stile è istituzionale, preciso e analitico. Non divagare.

Quando ricevi un asset, genera un segnale seguendo rigorosamente questo protocollo:

🟢 **STRATEGIA: BUY / LONG** o 🔴 **STRATEGIA: SELL / SHORT**
━━━━━━━━━━━━━━━━━━━━
💰 **ASSET:** [NOME ASSET]
💵 **ENTRY ZONE:** [PREZZO ATTUALE]
🎯 **TARGET 1:** [+2.00% circa]
🎯 **Target 2:** [+5.50% circa]
🛑 **STOP LOSS:** [-3.20% circa]
━━━━━━━━━━━━━━━━━━━━
⚡ **LEVA CONSIGLIATA:** 10x / 20x (Cross)
📊 **ANALISI TECNICA:** [Analisi dettagliata su RSI, Supporti/Resistenze e Volumi]

⚠️ *Nota: Gestione del rischio al 1-2% del capitale. Non è un consiglio finanziario.*
🔗 **Canale Ufficiale:** https://t.me/TradingAI_it
"""

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.2 # Mantiene le risposte precise e meno casuali
        )
        risposta = completion.choices[0].message.content
        bot.reply_to(message, risposta, parse_mode="Markdown")
    except Exception as e:
        print(f"Errore durante l'elaborazione: {e}")

# --- AVVIO MULTI-THREAD ---
if __name__ == "__main__":
    # Avvia il web server in un thread separato
    t = Thread(target=run)
    t.start()
    
    # Avvia il bot Telegram
    print("Sistema TradingAI-it connesso e operativo.")
    bot.infinity_polling()
