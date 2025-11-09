import os
import json
import random
import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
USER_DATA_FILE = os.path.join(BASE_DIR, "user_data.json")

# === Utility functions ===
def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === Load data ===
PHRASES = load_json("phrases.json")
GRAMMAR = load_json("grammar.json")
WORDS = load_json("words_tasks.json")
READING = load_json("reading_tasks.json")

user_data = load_user_data()

# === Topics for Quizlet words ===
topics = {
    "🌿 Адам және өмір": {
        "🫀 Дененің бөліктері": "https://quizlet.com/kz/1097300479/anatilдененің-бөліктері-части-тела-flash-cards/",
        "👨‍👩‍👧‍👦 Отбасы": "https://quizlet.com/kz/1097570867/anatil-отбасы-семья-flash-cards/",
        "👗 Киім": "https://quizlet.com/kz/1097575466/anatil-киім-одежда-flash-cards/",
        "💼 Кәсіптер": "https://quizlet.com/kz/1097575460/anatil-кәсіптер-профессии-flash-cards/",
        "😊 Эмоциялар": "https://quizlet.com/kz/1097582619/anatilэмоциялар-эмоции-flash-cards/",
        "🎭 Сипаттау": "https://quizlet.com/kz/1097582616/anatilсипаттау-описание-человека-flash-cards/",
        "🧠 Мінез-құлық": "https://quizlet.com/kz/1097616655/anatil-мінез-құлық-характер-и-поведение-flash-cards/"
    },
    "🌤 Табиғат және қоршаған орта": {
        "🐾 Жануарлар": "https://quizlet.com/kz/1101728652/",
        "🌿 Өсімдіктер": "https://quizlet.com/1101729865/",
        "🌦 Ауа райы": "https://quizlet.com/kz/1101730857/",
        "🗺 География": "https://quizlet.com/1101731617/",
        "❄️ Маусымдар": "https://quizlet.com/kz/1101732541/",
        "🌋 Табиғи апаттар": "https://quizlet.com/kz/1101733487/"
    }
}

# === Main menu ===
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📚 Сөздер", callback_data="menu_words")
    kb.button(text="✏️ Грамматика", callback_data="menu_grammar")
    kb.button(text="📖 Чтение", callback_data="menu_reading")
    kb.button(text="🧠 Задания", callback_data="menu_tasks")
    kb.button(text="📈 Прогресс", callback_data="menu_progress")
    kb.adjust(2, 2)
    return kb.as_markup()

# === Start ===
@dp.message(Command("start"))
async def start(message: Message):
    hour = datetime.datetime.now().hour
    greeting = "🌅 Қайырлы таң!" if hour < 12 else ("🌇 Қайырлы кеш!" if hour < 18 else "🌙 Қайырлы түн!")
    phrase = random.choice(PHRASES)["kz"] if PHRASES else "Білім — табысқа бастар жол."
    await message.answer(
        f"✨ *AnaTili Bot 🇰🇿*\n{greeting}\n\n"
        f"💬 Күннің дәйексөзі:\n_{phrase}_\n\n"
        "📚 Сөздер — Quizlet сілтемелері\n"
        "✏️ Грамматика — ережелер мен бейне\n"
        "📖 Чтение — мәтіндер деңгеймен\n"
        "📈 Прогресс — сенің жетістігің",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# === Words menu ===
@dp.callback_query(F.data == "menu_words")
async def show_topics(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for t in topics.keys():
        kb.button(text=t, callback_data=f"topic|{t}")
    kb.button(text="⬅️ Артқа", callback_data="menu_back")
    kb.adjust(1)
    await call.message.edit_text("📘 *Quizlet тақырыптары:*", parse_mode="Markdown", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("topic|"))
async def show_subtopics(call: CallbackQuery):
    topic_name = call.data.split("|")[1]
    subtopics = topics[topic_name]
    kb = InlineKeyboardBuilder()
    for sub, link in subtopics.items():
        kb.button(text=sub, url=link)
    kb.button(text="⬅️ Артқа", callback_data="menu_words")
    kb.adjust(1)
    await call.message.edit_text(f"✨ *{topic_name}* тақырыптары:", parse_mode="Markdown", reply_markup=kb.as_markup())

# === Grammar menu ===
@dp.callback_query(F.data == "menu_grammar")
async def show_grammar_menu(call: CallbackQuery):
    grammar = load_json("grammar.json")
    kb = InlineKeyboardBuilder()
    for i, item in enumerate(grammar):
        kb.button(text=item["title"], callback_data=f"grammar|{i}")
    kb.button(text="⬅️ Артқа", callback_data="menu_back")
    kb.adjust(1)
    await call.message.edit_text("📘 *Грамматика тақырыптары:*", parse_mode="Markdown", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("grammar|"))
async def show_grammar_topic(call: CallbackQuery):
    idx = int(call.data.split("|")[1])
    grammar = load_json("grammar.json")
    item = grammar[idx]
    kb = InlineKeyboardBuilder()
    kb.button(text="📖 Оқу", callback_data=f"grammar_file|{idx}")
    youtube_links = item.get("youtube")
    if youtube_links:
        if isinstance(youtube_links, list):
            for i, link in enumerate(youtube_links, start=1):
                kb.button(text=f"🎥 Видео {i}", url=link)
        else:
            kb.button(text="🎥 Видео", url=youtube_links)
    kb.button(text="⬅️ Артқа", callback_data="menu_grammar")
    kb.adjust(1)
    await call.message.edit_text(
        f"🧩 <b>{item['title']}</b>\n\n{item['description']}",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data.startswith("grammar_file|"))
async def open_grammar_file(call: CallbackQuery):
    idx = int(call.data.split("|")[1])
    grammar = load_json("grammar.json")
    item = grammar[idx]
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Артқа", callback_data=f"grammar|{idx}")
    kb.adjust(1)
    await call.message.edit_text(f"📘 <b>{item['title']}</b>\n\n{item['file_text']}", parse_mode="HTML", reply_markup=kb.as_markup())

# === Reading menu ===
@dp.callback_query(F.data == "menu_reading")
async def show_reading_levels(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for i, topic in enumerate(READING):
        kb.button(text=topic["title"], callback_data=f"reading_topic|{i}")
    kb.button(text="⬅️ Артқа", callback_data="menu_back")
    kb.adjust(1)
    await call.message.edit_text("📖 *Чтение:*", parse_mode="Markdown", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("reading_topic|"))
async def reading_topic(call: CallbackQuery):
    idx = int(call.data.split("|")[1])
    topic = READING[idx]
    kb = InlineKeyboardBuilder()
    kb.button(text="▶️ Бастау", callback_data=f"task_reading_question|{idx}|0")
    kb.button(text="⬅️ Артқа", callback_data="menu_reading")
    kb.adjust(1)
    await call.message.edit_text(f"📘 <b>{topic['title']}</b>\n\nМәтінді оқып, сұрақтарға жауап бер.", parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("task_reading_question|"))
async def reading_question(call: CallbackQuery):
    _, topic_idx, task_idx = call.data.split("|")
    topic_idx, task_idx = int(topic_idx), int(task_idx)
    reading = load_json("reading_tasks.json")
    topic = reading[topic_idx]
    task = topic["tasks"][task_idx]
    kb = InlineKeyboardBuilder()
    for opt in task["options"]:
        kb.button(text=opt, callback_data=f"task_reading_answer|{topic_idx}|{task_idx}|{opt}")
    kb.button(text="⬅️ Артқа", callback_data="task_reading")
    kb.adjust(1)
    await call.message.edit_text(f"📖 <b>{task['question']}</b>", parse_mode="HTML", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("task_reading_answer|"))
async def reading_answer(call: CallbackQuery):
    _, topic_idx, task_idx, chosen = call.data.split("|")
    topic_idx, task_idx = int(topic_idx), int(task_idx)
    reading = load_json("reading_tasks.json")
    topic = reading[topic_idx]
    task = topic["tasks"][task_idx]
    uid = str(call.from_user.id)
    user = get_user(uid)

    correct = (chosen == task["answer"])
    if correct:
        user["xp"] += 10
        user["score"] += 1
        text = f"✅ Дұрыс! *{task['answer']}* (+10 XP)"
        next_idx = task_idx + 1
    else:
        text = f"❌ Қате. Дұрыс жауап: *{task['answer']}*"
        next_idx = task_idx

    save_user_data(user_data)

    kb = InlineKeyboardBuilder()
    if not correct:
        kb.button(text="🔄 Қайтадан", callback_data=f"task_reading_question|{topic_idx}|{task_idx}")
    elif next_idx < len(topic["tasks"]):
        kb.button(text="▶️ Келесі", callback_data=f"task_reading_question|{topic_idx}|{next_idx}")
    else:
        kb.button(text="✅ Аяқтау", callback_data="task_reading")
    kb.button(text="⬅️ Артқа", callback_data="task_reading")
    kb.adjust(1)
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

# === Задания menu ===
@dp.callback_query(F.data == "menu_tasks")
async def menu_tasks(call: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🧩 Сөздер", callback_data="task_words")
    kb.button(text="📘 Грамматика", callback_data="task_grammar")
    kb.button(text="📖 Чтение", callback_data="task_reading")
    kb.button(text="⬅️ Артқа", callback_data="menu_back")
    kb.adjust(2, 1)
    await call.message.edit_text(
        "🧠 *Тапсырмалар бөлімі*\n\n"
        "🧩 Сөздер — сөздік тесттер\n"
        "📘 Грамматика — сұрақтарға жауап беріңіз\n"
        "📖 Чтение — мәтіндермен жұмыс\n",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

# === User data helper ===
def get_user(uid: str):
    if uid not in user_data:
        user_data[uid] = {
            "used_words": [],
            "used_grammar": [],
            "used_reading": {},
            "score": 0,
            "xp": 0
        }
    user_data[uid].setdefault("used_words", [])
    user_data[uid].setdefault("used_grammar", [])
    user_data[uid].setdefault("used_reading", {})
    user_data[uid].setdefault("score", 0)
    user_data[uid].setdefault("xp", 0)
    return user_data[uid]

# === Words tasks ===
@dp.callback_query(F.data == "task_words")
async def task_words(call: CallbackQuery):
    data = WORDS.get("words_tasks", [])
    uid = str(call.from_user.id)
    user = get_user(uid)

    available = [i for i, q in enumerate(data) if q["question"] not in user["used_words"]]
    if not available:
        await call.message.edit_text("✅ Барлық сөздер сұрақтары өтілді!", reply_markup=main_menu())
        return

    q_index = random.choice(available)
    q = data[q_index]
    user["used_words"].append(q["question"])
    save_user_data(user_data)

    kb = InlineKeyboardBuilder()
    for opt_index, opt in enumerate(q["options"]):
        kb.button(text=opt, callback_data=f"task_words_answer|{q_index}|{opt_index}")
    kb.button(text="⬅️ Артқа", callback_data="menu_tasks")
    await call.message.edit_text(f"🧩 *{q['question']}*", parse_mode="Markdown", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("task_words_answer|"))
async def task_words_answer(call: CallbackQuery):
    _, q_index, opt_index = call.data.split("|")
    q_index, opt_index = int(q_index), int(opt_index)
    q = WORDS["words_tasks"][q_index]
    chosen = q["options"][opt_index]
    correct = q["correct"]

    uid = str(call.from_user.id)
    user = get_user(uid)

    if chosen == correct:
        user["xp"] += 10
        user["score"] += 1
        text = f"✅ Дұрыс! *{correct}* (+10 XP)"
    else:
        text = f"❌ Қате. Дұрыс жауап: *{correct}*"

    save_user_data(user_data)

    kb = InlineKeyboardBuilder()
    if chosen != correct:
        kb.button(text="🔄 Қайтадан", callback_data="task_words")
    kb.button(text="▶️ Келесі", callback_data="task_words")
    kb.button(text="⬅️ Артқа", callback_data="menu_tasks")
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

# === Grammar tasks ===
@dp.callback_query(F.data == "task_grammar")
async def task_grammar(call: CallbackQuery):
    data = load_json("grammar_tasks.json")
    uid = str(call.from_user.id)
    user = get_user(uid)

    available = [i for i, q in enumerate(data) if q["question"] not in user["used_grammar"]]
    if not available:
        await call.message.edit_text("✅ Барлық грамматика сұрақтары өтілді!", reply_markup=main_menu())
        return

    q_index = random.choice(available)
    q = data[q_index]
    user["used_grammar"].append(q["question"])
    save_user_data(user_data)

    kb = InlineKeyboardBuilder()
    for opt_index, opt in enumerate(q["options"]):
        kb.button(text=opt, callback_data=f"task_grammar_answer|{q_index}|{opt_index}")
    kb.button(text="⬅️ Артқа", callback_data="menu_tasks")
    await call.message.edit_text(f"📘 *{q['question']}*", parse_mode="Markdown", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("task_grammar_answer|"))
async def task_grammar_answer(call: CallbackQuery):
    _, q_index, opt_index = call.data.split("|")
    q_index, opt_index = int(q_index), int(opt_index)
    data = load_json("grammar_tasks.json")
    q = data[q_index]
    chosen = q["options"][opt_index]
    correct = q["answer"]

    uid = str(call.from_user.id)
    user = get_user(uid)

    if chosen == correct:
        user["xp"] += 10
        user["score"] += 1
        text = f"✅ Дұрыс! *{correct}* (+10 XP)"
    else:
        text = f"❌ Қате. Дұрыс жауап: *{correct}*"

    save_user_data(user_data)

    kb = InlineKeyboardBuilder()
    if chosen != correct:
        kb.button(text="🔄 Қайтадан", callback_data="task_grammar")
    kb.button(text="▶️ Келесі", callback_data="task_grammar")
    kb.button(text="⬅️ Артқа", callback_data="menu_tasks")
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

# === Progress ===
@dp.callback_query(F.data == "menu_progress")
async def progress(call: CallbackQuery):
    uid = str(call.message.chat.id)
    d = get_user(uid)
    lvl = "🥉 Бастауыш" if d["xp"] < 50 else "🥈 Орта" if d["xp"] < 150 else "🥇 Жетік"
    bar = "█" * min(10, d["xp"] // 10) + "░" * (10 - min(10, d["xp"] // 10))
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Артқы", callback_data="menu_back")
    await call.message.edit_text(
        f"📊 *Сенің нәтижелерің:*\n\n"
        f"🏆 Ұпай: {d['score']}\n🔥 XP: {d['xp']}\n{bar}\n📈 Деңгей: {lvl}",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

# === Back button ===
@dp.callback_query(F.data == "menu_back")
async def go_back(call: CallbackQuery):
    await call.message.edit_text("🏠 *Басты меню*", parse_mode="Markdown", reply_markup=main_menu())

# === Run bot ===
async def main():
    print("🚀 Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
