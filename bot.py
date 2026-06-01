import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SYSTEM_PROMPT = """Ты — AI-ассистент лофт-пространства. Ты помогаешь клиентам и управляющим.

Ты знаешь следующее о заведении:
- Почасовая аренда комнат: от 500 ₽/час в будни, от 700 ₽/час в выходные
- В аренду входит: PlayStation 5, настольные игры, чай/кофе/вода
- Есть караоке-зал, кухня, зона отдыха
- Бронирование: аванс 30%, отмена бесплатна за 24 часа
- Работаем ежедневно с 12:00 до 02:00

Ты умеешь:
1. Отвечать на вопросы клиентов о ценах, услугах, бронировании
2. Придумывать идеи тематических вечеров и мероприятий
3. Писать посты для ВКонтакте и других соцсетей
4. Помогать управляющему с регламентами и скриптами для персонала
5. Генерировать идеи акций и специальных предложений

Отвечай дружелюбно, по-русски, коротко и по делу. Используй эмодзи умеренно.
Если не знаешь точного ответа — предложи уточнить у администратора."""


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
        }
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]


user_histories = {}

QUICK_BUTTONS = [
    ["💰 Цены и аренда", "🎮 Что входит?"],
    ["📅 Забронировать", "✨ Идея вечеринки"],
    ["📱 Пост для соцсетей", "📋 Скрипт для персонала"]
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    markup = ReplyKeyboardMarkup(QUICK_BUTTONS, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я AI-ассистент вашего лофта 🏠\n\n"
        "Могу ответить на вопросы клиентов, придумать идею мероприятия "
        "или написать пост для соцсетей.\n\n"
        "Выберите тему или напишите свой вопрос:",
        reply_markup=markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    button_map = {
        "💰 Цены и аренда": "Расскажи подробно о ценах и вариантах аренды",
        "🎮 Что входит?": "Что входит в стоимость аренды?",
        "📅 Забронировать": "Как забронировать комнату и внести предоплату?",
        "✨ Идея вечеринки": "Придумай оригинальную идею тематического вечера для компании 6-10 человек",
        "📱 Пост для соцсетей": "Напиши яркий пост для ВКонтакте о нашем лофте",
        "📋 Скрипт для персонала": "Напиши скрипт для администратора: как встречать гостей и отвечать на типичные вопросы"
    }
    actual_message = button_map.get(user_message, user_message)

    if user_id not in user_histories:
        user_histories[user_id] = []

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    try:
        answer = ask_groq(actual_message, user_histories[user_id])
        user_histories[user_id].append({"role": "user", "content": actual_message})
        user_histories[user_id].append({"role": "assistant", "content": answer})
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(
            "Упс, что-то пошло не так 😔 Попробуйте ещё раз через минуту."
        )


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
