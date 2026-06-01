import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SYSTEM_PROMPT = """Ты — AI-ассистент лофта PARTY TIME в Санкт-Петербурге. Ты помогаешь клиентам с выбором комнаты, бронированием и вопросами о заведении.

КОМНАТЫ И ЦЕНЫ (аренда за час):
- Бэтмен — 1000 руб/час. Тёмная атмосфера, стиль Готэма, идеально для тематических вечеринок
- Поп-арт — 1200 руб/час. Яркий стиль, позитивная энергетика, отлично для дней рождения
- Диско — 1400 руб/час. Зеркальный шар, ретро-атмосфера, для тех кто любит танцевать
- Театр — 1600 руб/час. Самая премиальная комната, изысканный интерьер, для особых событий

В СТОИМОСТЬ ВХОДИТ: настольные игры, караоке, красивая сервировка стола.
Время работы: ежедневно с 12:00 до 06:00
Бронирование: через этого бота или по телефону +7 996 414-61-06

ЕСЛИ КЛИЕНТ ХОЧЕТ ЗАБРОНИРОВАТЬ — уточни: имя, комнату, дату, время, количество гостей.
Отвечай дружелюбно, по-русски, коротко и по делу."""


def ask_groq(user_message: str, history: list) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": user_message})
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        },
        timeout=30
    )
    print(f"Groq status: {response.status_code}")
    print(f"Groq response: {response.text[:200]}")
    data = response.json()
    return data["choices"][0]["message"]["content"]


user_histories = {}

QUICK_BUTTONS = [
    ["Цены на комнаты", "Какую комнату выбрать?"],
    ["Забронировать", "Что входит в аренду?"],
    ["Идея для вечеринки", "Пост для соцсетей"]
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    markup = ReplyKeyboardMarkup(QUICK_BUTTONS, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Добро пожаловать в PARTY TIME!\n\n"
        "У нас 4 уникальные комнаты:\n"
        "Бэтмен, Поп-арт, Диско, Театр\n\n"
        "Работаем ежедневно с 12:00 до 06:00\n\n"
        "Чем могу помочь?",
        reply_markup=markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    button_map = {
        "Цены на комнаты": "Расскажи подробно о всех комнатах и ценах",
        "Какую комнату выбрать?": "Помоги выбрать комнату, задай уточняющие вопросы",
        "Забронировать": "Хочу забронировать комнату",
        "Что входит в аренду?": "Что входит в стоимость аренды?",
        "Идея для вечеринки": "Придумай идею тематической вечеринки",
        "Пост для соцсетей": "Напиши яркий пост для ВКонтакте о лофте PARTY TIME"
    }
    actual_message = button_map.get(user_message, user_message)

    if user_id not in user_histories:
        user_histories[user_id] = []

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        answer = ask_groq(actual_message, user_histories[user_id])
        user_histories[user_id].append({"role": "user", "content": actual_message})
        user_histories[user_id].append({"role": "assistant", "content": answer})
        await update.message.reply_text(answer)
    except Exception as e:
        print(f"ERROR: {e}")
        await update.message.reply_text(f"Ошибка: {str(e)[:100]}")


def main():
    print(f"Token exists: {bool(TELEGRAM_TOKEN)}")
    print(f"Groq key exists: {bool(GROQ_API_KEY)}")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
