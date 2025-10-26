import telebot
from telebot import types
import json, os, random, datetime

TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    print("❌ Error: TOKEN not found in environment variables")
    exit()

bot = telebot.TeleBot(TOKEN)

# === ФАЙЛЫ И ПАПКИ ===
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
USER_DATA_FILE = os.path.join(os.path.dirname(__file__), 'user_data.json')

def load_json(name):
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

WORDS = load_json('words.json')
PHRASES = load_json('phrases.json')
GRAMMAR = load_json('grammar.json')

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_data = load_user_data()

# === ТЕМЫ QUIZLET ===
topics = {
    "🌿 Адам және өмір": {
        "🫀 Дененің бөліктері": "https://quizlet.com/kz/1097300479/anatilдененің-бөліктері-части-тела-flash-cards/",
        "👨‍👩‍👧‍👦 Отбасы": "https://quizlet.com/kz/1097570867/anatil-отбасы-семья-flash-cards/",
        "👗 Киім": "https://quizlet.com/kz/1097575466/anatil-киім-одежда-flash-cards/",
        "💼 Кәсіптер": "https://quizlet.com/kz/1097575460/anatil-кәсіптер-профессии-flash-cards/?new",
        "😊 Эмоциялар": "https://quizlet.com/kz/1097582619/anatilэмоциялар-эмоции-flash-cards/?new",
        "🎭 Сипаттау": "https://quizlet.com/kz/1097582616/anatilсипаттау-описание-человека-flash-cards/?new",
        "🧠 Мінез-құлық": "https://quizlet.com/kz/1097616655/anatil-мінез-құлық-характер-и-поведение-flash-cards/?new"
    }
}

# === СТАРТ ===
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📚 Темы"),
        types.KeyboardButton("🧠 Викторина"),
        types.KeyboardButton("💬 Фраза дня"),
        types.KeyboardButton("📈 Прогресс")
    )
    now = datetime.datetime.now().hour
    greeting = "🌅 Қайырлы таң!" if now < 12 else ("🌇 Қайырлы кеш!" if now < 18 else "🌙 Қайырлы түн!")
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

# === ФРАЗА ДНЯ ===
@bot.message_handler(func=lambda m: m.text == "💬 Фраза дня")
def send_phrase(message):
    if not PHRASES:
        return bot.send_message(message.chat.id, "⚠️ Фразалар базасы бос.")
    p = random.choice(PHRASES)
    text = (
        f"💫 *Бүгінгі фраза:*\n\n"
        f"🇰🇿 {p['kz']}\n"
        f"🇷🇺 {p['ru']}\n\n"
        f"🌟 _Мысалы:_ {p.get('example', 'жоқ')}"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# === QUIZLET ТЕМЫ ===
@bot.message_handler(func=lambda m: m.text == "📚 Темы")
def show_topics(message):
    markup = types.InlineKeyboardMarkup()
    for t in topics.keys():
        markup.add(types.InlineKeyboardButton(t, callback_data=f"topic|{t}"))
    bot.send_message(message.chat.id, "📘 *Quizlet тақырыптары:*", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("topic|"))
def show_subtopics(call):
    topic_name = call.data.split("|")[1]
    subtopics = topics[topic_name]
    markup = types.InlineKeyboardMarkup()
    for sub, link in subtopics.items():
        markup.add(types.InlineKeyboardButton(sub, url=link))
    bot.send_message(call.message.chat.id, f"✨ *{topic_name}* тақырыптары:", parse_mode="Markdown", reply_markup=markup)

# === ВИКТОРИНА (улучшенная) ===
@bot.message_handler(func=lambda m: m.text == "🧠 Викторина")
def start_quiz(message):
    send_quiz_question(message.chat.id)

def send_quiz_question(chat_id):
    if not WORDS:
        bot.send_message(chat_id, "⚠️ Сөздер базасы бос.")
        return
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
    user_id = str(call.message.chat.id)
    if user_id not in user_data:
        user_data[user_id] = {"known": [], "score": 0, "xp": 0}
    if "xp" not in user_data[user_id]:
        user_data[user_id]["xp"] = 0



    if chosen == correct:
        user_data[user_id]["score"] += 1
        user_data[user_id]["xp"] += 10
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
def quiz_continue_or_stop(call):
    user_id = str(call.message.chat.id)
    if call.data == "quiz_next":
        send_quiz_question(call.message.chat.id)
    else:
        data = user_data.get(user_id, {"score": 0, "xp": 0})
        xp = data["xp"]
        lvl = "🥉" if xp < 50 else ("🥈" if xp < 150 else "🥇")
        progress = min(10, xp // 10)
        bar = "█" * progress + "░" * (10 - progress)
        bot.send_message(
            call.message.chat.id,
            f"🏁 Викторина аяқталды!\n\n"
            f"📊 Прогресс: {bar} {xp}%\n"
            f"🏆 Жалпы ұпай: {data['score']}\n"
            f"🔥 Деңгей: {lvl}",
            parse_mode="Markdown"
        )

# === ПРОГРЕСС ===
@bot.message_handler(func=lambda m: m.text == "📈 Прогресс")
def stats(message):
    user_id = str(message.chat.id)
    data = user_data.get(user_id, {"known": [], "score": 0, "xp": 0})
    lvl = "🥉 Бастауыш" if data["xp"] < 50 else "🥈 Орта" if data["xp"] < 150 else "🥇 Жетік"
    progress = min(10, data["xp"] // 10)
    bar = "█" * progress + "░" * (10 - progress)
    bot.send_message(
        message.chat.id,
        f"📊 *Сенің нәтижелерің:*\n\n"
        f"📘 Үйренген сөздер: {len(data['known'])}\n"
        f"🏆 Викторина ұпайы: {data['score']}\n"
        f"🔥 XP: {data['xp']}\n"
        f"{bar} ({data['xp']} XP)\n"
        f"📈 Деңгей: {lvl}",
        parse_mode="Markdown"
    )

print("🚀 AnaTili Bot v2.0 is running...")
bot.polling(none_stop=True)
