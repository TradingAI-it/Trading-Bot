import os
import telebot
import threading
from flask import Flask
from groq import Groq

# --- SERVER PER RENDER ---
app = Flask('')
@app.route('/')
def home():
    return "Server Online"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# --- CONFIGURAZIONE ---
TOKEN = '8570081459:AAFl_p5dmdptTM_56kKpA0x2t3AxROV-k7Jc'
CHAT_ID = '1470247172'
# Prendiamo la chiave dalle variabili di Render
GROQ_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(TOKEN)

# --- TEST IMMEDIATO ---
print("--- AVVIO SISTEMA ---")
try:
    bot.send_message(CHAT_ID, "🔔 TEST: Il bot sta provando a connettersi...")
    print("✅ Messaggio di test inviato su Telegram!")
except Exception as e:
    print(f"❌ Errore Telegram: {e}")

# --- RISPOSTA AI TUOI MESSAGGI ---
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Ricevuto! Sono attivo e sto monitorando i mercati. Appena c'è una news importante ti avviso qui.")

# --- AVVIO ---
if __name__ == "__main__":
    # Avvia Flask
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("🚀 Bot in ascolto su Telegram...")
    bot.infinity_polling()
