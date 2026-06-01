# AI-ассистент для лофта — инструкция по запуску

## Файлы проекта
- bot.py — основной код бота
- requirements.txt — зависимости
- Procfile — команда для Railway

## Запуск на Railway (бесплатно)

### 1. Подготовка
Зарегистрируйся на railway.app через GitHub.
Если нет GitHub — зарегистрируйся сначала на github.com (бесплатно).

### 2. Загрузка кода
1. Создай аккаунт на github.com
2. Нажми "New repository" → назови "loft-bot" → Create
3. Загрузи три файла: bot.py, requirements.txt, Procfile

### 3. Деплой на Railway
1. Зайди на railway.app → New Project → Deploy from GitHub
2. Выбери репозиторий loft-bot
3. Перейди в Variables и добавь две переменные:
   - TELEGRAM_TOKEN = (токен от @BotFather)
   - GROQ_API_KEY = (ключ от console.groq.com)
4. Нажми Deploy

### 4. Готово!
Бот запустится автоматически и будет работать 24/7.
Открой Telegram, найди своего бота и напиши /start

## Настройка под конкретный лофт
В файле bot.py найди переменную SYSTEM_PROMPT и замени:
- Цены на реальные цены заведения
- Услуги на реальный список услуг
- Время работы на реальное расписание
