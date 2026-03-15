import telebot
import feedparser
import time
from groq import Groq

# --- DATI CONFIGURATI ---
TOKEN = '8570081459:AAFl_p5dmdptTM_56kKpA0x2t3AxROVk7Jc'
CHAT_ID = '1470247172'
GROQ_KEY = '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'

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
    SYSTEM: You are a professional Hedge Fund Trader.
    INPUT: News: '{title}'
    TASK:
    1. Analyze if this news is a HIGH IMPACT event (likely to move the asset by AT LEAST 1%).
    2. If it's a minor news or low impact, reply ONLY with 'SKIP'.
    3. If it's a major event, provide a signal: 🟢 BUY [TICKER] or 🔴 SELL [TICKER]
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
    bot.send_message(CHAT_ID, "✅ Sistema AI Online su Render. Monitoraggio attivo.")
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
                print(f"Errore: {e}")
        time.sleep(120)

if __name__ == "__main__":
    monitor()
