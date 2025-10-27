import os
import json
import random
import datetime
import telebot
from telebot import types
from flask import Flask, request

# === Токен бота ===
TOKEN = "7690089205:AAGv__UITt-E2Q1OYTQYzgI8F8lBROCttHM"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# === Пути к файлам ===
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
USER_DATA_FILE = os.path.join(BASE_DIR, "user_data.json")

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

WORDS = load_json("words.json")
PHRASES = load_json("phrases.json")
GRAMMAR = load_json("grammar.json")

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_data = load_user_data()

topics = {
    "🌿 Адам және өмір": {
        "🫀 Дененің бөліктері": "https://quizlet.com/kz/1097300479/anatilдененің-бөліктері-части-тела-flash-cards/",
        "👨‍👩‍👧‍👦 Отбасы": "https://quizlet.com/kz/1097570867/anatil-отбасы-семья-flash-cards/",
        "👗 Киім": "https://quizlet.com/kz/1097575466/anatil-киім-одежда-flash-cards/",
        "💼 Кәсіптер": "https://quizlet.com/kz/1097575460/anatil-кәсіптер-профессии-flash-cards/",
        "😊 Эмоциялар": "https://quizlet.com/kz/1097582619/anatilэмоциялар-эмоции-flash-cards/",
        "🎭 Сипаттау": "https://quizlet.com/kz/1097582616/anatilсипаттау-описание-человека-flash-cards/",
        "🧠 Мінез-құлық": "https://quizlet.com/kz/1097616655/anatil-мінез-құлық-характер-и-поведение-flash-cards/"
    }
}

# === Команды ===
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📚 Темы"),
        types.KeyboardButton("🧠 Викторина"),
        types.KeyboardButton("💬 Фраза дня"),
        types.KeyboardButton("📈 Прогресс")
    )
    hour = datetime.datetime.now().hour
    greeting = "🌅 Қайырлы таң!" if hour < 12 else ("🌇 Қайырлы кеш!" if hour < 18 else "🌙 Қайырлы түн!")
    phrase = random.choice(PHRASES)["kz"] if PHRASES else "Білім — табысқа бастар жол."
    bot.send_message(
        message.chat.id,
        f"✨ *AnaTili Bot 🇰🇿*\n{greeting}\n\n"
        f"💬 Күннің фразасы:\n_{phrase}_\n\n"
        "📚 Темы — Quizlet сілтемелері\n"
        "🧠 Викторина — жаттығулар мен ұпайлар\n"
        "📈 Прогресс — сенің деңгейіңді көру",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "💬 Фраза дня")
def phrase_day(message):
    if not PHRASES:
        return bot.send_message(message.chat.id, "⚠️ Фразалар базасы бос.")
    p = random.choice(PHRASES)
    bot.send_message(
        message.chat.id,
        f"💫 *Бүгінгі фраза:*\n\n"
        f"🇰🇿 {p['kz']}\n"
        f"🇷🇺 {p['ru']}\n\n"
        f"🌟 _Мысалы:_ {p.get('example', 'жоқ')}",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "📚 Темы")
def show_topics(message):
    markup = types.InlineKeyboardMarkup()
    for t in topics.keys():
        markup.add(types.InlineKeyboardButton(t, callback_data=f"topic|{t}"))
    bot.send_message(message.chat.id, "📘 *Quizlet тақырыптары:*", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("topic|"))
def show_subtopics(call):
    topic_name = call.data.split("|")[1]
    subtopics = topics[topic_name]
    markup = types.InlineKeyboardMarkup()
    for sub, link in subtopics.items():
        markup.add(types.InlineKeyboardButton(sub, url=link))
    bot.send_message(call.message.chat.id, f"✨ *{topic_name}* тақырыптары:", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🧠 Викторина")
def quiz(message):
    send_quiz(message.chat.id)

def send_quiz(chat_id):
    if not WORDS:
        return bot.send_message(chat_id, "⚠️ Сөздер базасы бос.")
    w = random.choice(WORDS)
    correct = w["ru"]
    options = [correct]
    while len(options) < 4:
        opt = random.choice(WORDS)["ru"]
        if opt not in options:
            options.append(opt)
    random.shuffle(options)
    markup = types.InlineKeyboardMarkup()
    for opt in options:
        markup.add(types.InlineKeyboardButton(opt, callback_data=f"quiz|{w['kz']}|{opt}|{correct}"))
    bot.send_message(chat_id, f"🧠 *{w['kz']}* сөзінің аудармасы қандай?", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("quiz|"))
def quiz_answer(call):
    _, kz, chosen, correct = call.data.split("|")
    uid = str(call.message.chat.id)
    if uid not in user_data:
        user_data[uid] = {"known": [], "score": 0, "xp": 0}
    if chosen == correct:
        user_data[uid]["score"] += 1
        user_data[uid]["xp"] += 10
        msg = f"✅ Дұрыс! *{kz}* = {correct}\n+10 XP 🔥"
    else:
        msg = f"❌ Қате. Дұрыс жауап: *{correct}*"
    save_user_data(user_data)
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("▶️ Жалғастыру", callback_data="quiz_next"),
        types.InlineKeyboardButton("⏹️ Тоқтату", callback_data="quiz_stop")
    )
    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data in ["quiz_next", "quiz_stop"])
def quiz_control(call):
    uid = str(call.message.chat.id)
    if call.data == "quiz_next":
        send_quiz(call.message.chat.id)
    else:
        data = user_data.get(uid, {"score": 0, "xp": 0})
        xp = data["xp"]
        lvl = "🥉" if xp < 50 else ("🥈" if xp < 150 else "🥇")
        bar = "█" * min(10, xp // 10) + "░" * (10 - min(10, xp // 10))
        bot.send_message(
            call.message.chat.id,
            f"🏁 Викторина аяқталды!\n\n📊 Прогресс: {bar} {xp} XP\n🏆 Ұпай: {data['score']}\n🔥 Деңгей: {lvl}",
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda m: m.text == "📈 Прогресс")
def progress(message):
    uid = str(message.chat.id)
    d = user_data.get(uid, {"known": [], "score": 0, "xp": 0})
    lvl = "🥉 Бастауыш" if d["xp"] < 50 else "🥈 Орта" if d["xp"] < 150 else "🥇 Жетік"
    bar = "█" * min(10, d["xp"] // 10) + "░" * (10 - min(10, d["xp"] // 10))
    bot.send_message(
        message.chat.id,
        f"📊 *Сенің нәтижелерің:*\n\n📘 Үйренген сөздер: {len(d['known'])}\n"
        f"🏆 Ұпай: {d['score']}\n🔥 XP: {d['xp']}\n{bar}\n📈 Деңгей: {lvl}",
        parse_mode="Markdown"
    )


# === Flask routes ===
@app.route("/", methods=["GET"])
def index():
    return "✅ KazLangBot is running!", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Webhook active ✅", 200

    if request.method == "POST":
        update = request.get_json(force=True, silent=True)
        if update:
            bot.process_new_updates([telebot.types.Update.de_json(update)])
        return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Server started on port {port}")
    app.run(host="0.0.0.0", port=port)
