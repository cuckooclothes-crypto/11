import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ==================== КОНФИГУРАЦИЯ ====================
BOT_TOKEN = "8617615907:AAEvE6tQZLwbd-Mmz_pPu2soVXpwD_crG4o"  # Замените на реальный токен
ADMIN_ID = 854447207  # Замените на ваш Telegram ID

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ==================== КЛАВИАТУРЫ ====================
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Восстановление")],
        [KeyboardButton(text="Гармония движения")],
        [KeyboardButton(text="Ресурсный код")],
        [KeyboardButton(text="Экспресс-обновление")],
        [KeyboardButton(text="Нейрофлоатинг")]
    ],
    resize_keyboard=True
)

complete_btn_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Программа пройдена")]],
    resize_keyboard=True
)

after_recommendations_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="◀️ Вернуться к выбору программ")],
        [KeyboardButton(text="💎 Оставить заявку на клубную карту")]
    ],
    resize_keyboard=True
)

back_to_main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="◀️ Вернуться к выбору программ")]],
    resize_keyboard=True
)

# ==================== СОСТОЯНИЯ ====================
class OrderStates(StatesGroup):
    waiting_for_contact = State()

# ==================== ХРАНИЛИЩЕ ====================
user_temp = {}

# ==================== ССЫЛКИ НА ПРАКТИКИ ====================
# 👇👇👇 ВСТАВЬТЕ ВАШИ ССЫЛКИ СЮДА 👇👇👇

# 1. ССЫЛКА НА ВИДЕО (общая для всех программ)
VIDEO_LINK = "https://t.me/c/2776024589/142"  # Замените на вашу ссылку

# 2. АУДИО ДЛЯ КАЖДОЙ ПРОГРАММЫ
# Вариант 1: можно использовать прямые ссылки на файлы в облаке
# Вариант 2: можно использовать file_id от Telegram (рекомендуется)

AUDIO_LINKS = {
    "Восстановление": "https://disk.yandex.ru/d/llMpx0DXxeADvA",      # Аудио для восстановления
    "Гармония движения": "https://disk.yandex.ru/d/6o9Ye4EQVpSmcw",   # Аудио для гармонии
    "Ресурсный код": "https://disk.yandex.ru/d/6o9Ye4EQVpSmcw",       # Аудио для ресурсного кода
    "Экспресс-обновление": "https://disk.yandex.ru/d/llMpx0DXxeADvA", # Аудио для экспресса
    "Нейрофлоатинг": "https://disk.yandex.ru/d/llMpx0DXxeADvA",       # Аудио для нейрофлоатинга
}

# Если у вас одинаковое аудио для нескольких программ, просто укажите одну ссылку:
# "Восстановление": "https://t.me/ваш_канал/101",
# "Гармония движения": "https://t.me/ваш_канал/101",  # то же аудио
# "Ресурсный код": "https://t.me/ваш_канал/102",      # другое аудио

# ==================== ДАННЫЕ ПРОГРАММ ====================
programs_data = {
    "Восстановление": {
        "description": (
            "🌿 <b>Программа «Восстановление»</b>\n\n"
            "Комплексная перезагрузка систем организма за один визит. Программа устраняет "
            "«информационный шум», обнуляет уровень кортизола и возвращает вас в состояние "
            "высокой продуктивности.\n\n"
            "📋 <b>Что входит в программу:</b>\n"
            "1️⃣ Диагностика на аппарате Lotus Onyx — оцифровка биоритмов и уровня стресса\n"
            "2️⃣ Коррекционная сессия с телом — работа с ведущим специалистом центра\n"
            "3️⃣ Глубокое погружение (на выбор по результатам диагностики) — флоатинг или детокс в японском модуле Iyashi Dome\n"
            "4️⃣ Нейро-настройка (на выбор по результатам диагностики) — капсула Somadome или нейромедитация в PrivateNap"
        ),
        "preparation": (
            "⚠️ <b>Важная подготовка к программе</b>\n\n"
            "Для максимального результата соблюдайте правила:\n\n"
            "☕ <b>Напитки:</b> За 2 часа до начала исключите кофе, крепкий чай, энергетики\n"
            "🍷 <b>Алкоголь:</b> Не употребляйте минимум 24 часа до визита\n"
            "🌸 <b>Цикл (для женщин):</b> Программа не проводится в период цикла (±2 дня)\n"
            "💊 <b>Медикаменты:</b> Сообщите специалисту об антидепрессантах или нейролептиках"
        )
    },
    "Гармония движения": {
        "description": (
            "🏃‍♂️ <b>Программа «Гармония движения»</b>\n\n"
            "Профессиональное восстановление и биохакинг для атлетов и активных людей. "
            "Программа помогает предотвратить травмы, снимает «мышечный панцирь» и балансирует "
            "нервную систему.\n\n"
            "📋 <b>Что входит в программу:</b>\n"
            "1️⃣ Функциональный аудит организма — диагностика Lotus Onyx\n"
            "2️⃣ Глубокий детокс — сеанс в японском модуле Iyashi Dome\n"
            "3️⃣ Мануальная коррекция — работа с ведущим специалистом\n"
            "4️⃣ Нейро-восстановление — PrivateNap или капсула Somadome"
        ),
        "preparation": (
            "⚠️ <b>Правила подготовки к программе</b>\n\n"
            "☕ <b>Напитки:</b> За 2 часа до начала исключите кофе, чай, предтренировочные комплексы\n"
            "🍷 <b>Алкоголь:</b> Полный запрет за 24 часа до визита\n"
            "🌸 <b>Цикл (для женщин):</b> Противопоказано в период цикла\n"
            "💊 <b>Фармакология:</b> Уведомите специалиста о принимаемых препаратах\n\n"
            "🌟 <i>Верните телу гармонию и ресурс для новых побед!</i>"
        )
    },
    "Ресурсный код": {
        "description": (
            "⚡ <b>Программа «Ресурсный код»</b>\n\n"
            "Стратегическая активация потенциала и запуск новых смыслов. Программа "
            "«взламывает» привычные сценарии мышления, расширяет пропускную способность "
            "вашей психики.\n\n"
            "📋 <b>Что входит в программу:</b>\n"
            "1️⃣ Функциональный аудит организма — диагностика Lotus Onyx\n"
            "2️⃣ Телесно-ориентированная деблокация — работа с телом и психосоматикой\n"
            "3️⃣ Биоинформационная коррекция — сеанс в модуле на базе Зеркал Козырева-Казначеева"
        ),
        "preparation": (
            "⚠️ <b>Подготовка к программе</b>\n\n"
            "☕ За 2 часа до начала исключите кофе, крепкий чай, энергетики\n"
            "🍷 Алкоголь — полный запрет за 24 часа\n"
            "🌸 Женщинам: программа не проводится в период цикла\n"
            "💊 Сообщите специалисту о принимаемых антидепрессантах или нейролептиках"
        )
    },
    "Экспресс-обновление": {
        "description": (
            "⚡ <b>Программа «Экспресс-обновление»</b>\n\n"
            "Быстрое возвращение в ресурс и эффективное снятие усталости. Экспресс-протокол "
            "для восстановления работоспособности «здесь и сейчас».\n\n"
            "📋 <b>Что входит в программу:</b>\n"
            "1️⃣ Функциональный аудит организма — диагностика Lotus Onyx\n"
            "2️⃣ Мануальная коррекция — снятие мышечных зажимов\n"
            "3️⃣ Нейро-восстановление — Somadome или PrivateNap\n"
            "4️⃣ Био-поддержка — кислородный бар с ароматерапией"
        ),
        "preparation": (
            "⚠️ <b>Подготовка к программе</b>\n\n"
            "☕ За 2 часа до начала исключите кофе, крепкий чай, энергетики\n"
            "🍷 Алкоголь — полный запрет за 24 часа\n"
            "🌸 Программа не проводится в период цикла\n"
            "💊 Сообщите специалисту о принимаемых медикаментах"
        )
    },
    "Нейрофлоатинг": {
        "description": (
            "🌊 <b>Программа «Нейрофлоатинг» с Михаилом Бирюковым</b> 🌊\n\n"
            "Глубинное обнуление и пересборка ресурсного состояния для лидеров. "
            "«Точка абсолютной тишины» в мире бесконечного шума.\n\n"
            "📋 <b>Этапы прохождения:</b>\n"
            "1️⃣ Теоретический модуль и настрой\n"
            "2️⃣ Цифровой чекап — диагностика Lotus Onyx\n"
            "3️⃣ Телесная нейрокоррекция — работа с Михаилом Бирюковым\n"
            "4️⃣ Погружение во Флоатинг — сенсорная депривация\n"
            "5️⃣ Психокоррекционная интеграция\n"
            "6️⃣ Кислородная терапия"
        ),
        "preparation": (
            "⚠️ <b>Правила подготовки</b>\n\n"
            "☕ За 2 часа до начала исключите тонизирующие напитки\n"
            "🍷 Алкоголь — полный запрет за 24 часа\n"
            "🌸 Программа не проводится в период цикла\n"
            "💊 Сообщите ментору об антидепрессантах или нейролептиках\n\n"
            "<i>Станьте хозяином своего состояния!</i>"
        )
    }
}


# ==================== РЕКОМЕНДАЦИИ ДЛЯ ПРОГРАММ ====================
def get_recommendations(program_name):
    """Возвращает рекомендации для конкретной программы"""
    
    recommendations = {
        "Восстановление": {
            "title": "🌱 <b>Ваша новая норма</b>",
            "rules": (
                "• 🔁 <b>Системность:</b> Выполняйте практики ежедневно (утром или вечером)\n"
                "• 📍 <b>Дисциплина:</b> Без перерывов для закрепления нейронных связей\n"
                "• 📔 <b>Осознанность:</b> Заведите Дневник наблюдений — фиксируйте изменения\n\n"
                "<i>Ваш ресурс — это ежедневная стратегия</i>"
            )
        },
        "Гармония движения": {
            "title": "🏃 <b>Ваша новая норма</b>",
            "rules": (
                "• 🔁 <b>Системность:</b> Практики каждый день (утром или вечером)\n"
                "• 📍 <b>Дисциплина:</b> Не делайте перерывов\n"
                "• 📔 <b>Дневник наблюдений:</b> Отслеживайте прогресс\n\n"
                "<i>Ваш ресурс — это ежедневная стратегия</i>"
            )
        },
        "Ресурсный код": {
            "title": "⚡ <b>Стабилизация после программы</b>",
            "rules": (
                "• 🔁 <b>Системность:</b> Практики ежедневно без перерывов\n"
                "• 📔 <b>Дневник наблюдений:</b> Обязательно фиксируйте инсайты и изменения\n\n"
                "<i>Раскройте свой истинный потенциал</i>"
            )
        },
        "Экспресс-обновление": {
            "title": "✨ <b>Удержание состояния бодрости</b>",
            "rules": (
                "• 🔁 <b>Системность:</b> Ежедневные практики (утро/вечер)\n"
                "• 📔 <b>Дневник наблюдений:</b> Фиксируйте уровень энергии и концентрации\n\n"
                "<i>Верните себе продуктивность за один визит</i>"
            )
        },
        "Нейрофлоатинг": {
            "title": "🧠 <b>Окно пластичности вашего мозга</b> ",
            "rules": (
                "• 🔁 <b>Системность:</b> Каждый день без исключений (утро/вечер)\n"
                "• 📔 <b>Дневник наблюдений:</b> Оцифруйте качественный скачок эффективности\n\n"
                "<i>Станьте хозяином своего состояния</i>"
            )
        }
    }
    
    rec = recommendations.get(program_name, recommendations["Восстановление"])
    
    # Получаем ссылку на аудио для конкретной программы
    audio_link = AUDIO_LINKS.get(program_name, AUDIO_LINKS["Восстановление"])
    
    daily_plan = (
        f"📋 <b>Ваш ежедневный план:</b>\n\n"
        f"🌬️ <b>1. Дыхательная практика</b> — Настройка вегетативной нервной системы\n"
        f"   👉 <a href='{VIDEO_LINK}'>📺 Смотреть видео-инструкцию</a>\n\n"
        f"🎧 <b>2. Нейромедитация</b> — Синхронизация работы полушарий\n"
        f"   👉 <a href='{audio_link}'>🎵 Слушать аудио</a>"
    )
    
    return rec["title"], rec["rules"], daily_plan


# ==================== ОБРАБОТЧИКИ ====================
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "<b>Добро пожаловать!</b>\n\n"
        "Пожалуйста, выберите забронированную вами программу:",
        parse_mode="HTML",
        reply_markup=main_menu_kb
    )


@dp.message(F.text.in_(list(programs_data.keys())))
async def show_program(message: types.Message):
    program_name = message.text
    data = programs_data[program_name]
    user_id = message.from_user.id
    user_temp[user_id] = {"program": program_name}
    
    await message.answer(data["description"], parse_mode="HTML")
    await message.answer(data["preparation"], parse_mode="HTML")
    await message.answer(
        "✅ <b>Нажмите кнопку ниже, когда пройдете программу</b>",
        parse_mode="HTML",
        reply_markup=complete_btn_kb
    )


@dp.message(F.text == "✅ Программа пройдена")
async def program_completed(message: types.Message):
    user_id = message.from_user.id
    program_name = user_temp.get(user_id, {}).get("program")
    
    if not program_name:
        await message.answer(
            "❓ Пожалуйста, сначала выберите программу из меню.",
            parse_mode="HTML",
            reply_markup=main_menu_kb
        )
        return
    
    title, rules, daily_plan = get_recommendations(program_name)
    
    await message.answer(
        f"{title}\n\n{rules}",
        parse_mode="HTML"
    )
    await message.answer(
        daily_plan,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await message.answer(
        "📌 <b>Выберите дальнейшее действие:</b>",
        parse_mode="HTML",
        reply_markup=after_recommendations_kb
    )


@dp.message(F.text == "◀️ Вернуться к выбору программ")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>Добро пожаловать!</b>\n\n"
        "Пожалуйста, выберите забронированную вами программу:",
        parse_mode="HTML",
        reply_markup=main_menu_kb
    )


@dp.message(F.text == "💎 Оставить заявку на клубную карту")
async def ask_contact(message: types.Message, state: FSMContext):
    await message.answer(
        "💎 <b>Оформление клубной карты</b> 💎\n\n"
        "Пожалуйста, отправьте ваши контактные данные одним сообщением:\n\n"
        "📞 <b>Пример:</b> <code>+7 123 456 78 90, Иван Иванов</code>\n\n"
        "Эти данные будут переданы администратору для связи с вами.",
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_for_contact)


@dp.message(OrderStates.waiting_for_contact)
async def receive_contact(message: types.Message, state: FSMContext):
    contact_info = message.text
    user = message.from_user
    user_id = user.id
    username = user.username or "Нет username"
    full_name = user.full_name
    program_name = user_temp.get(user_id, {}).get("program", "Не выбрана")
    
    admin_msg = (
        f"📩 <b>НОВАЯ ЗАЯВКА НА КЛУБНУЮ КАРТУ</b>\n\n"
        f"👤 <b>Имя:</b> {full_name}\n"
        f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        f"🔗 <b>Username:</b> @{username}\n"
        f"📞 <b>Контакт:</b> {contact_info}\n"
        f"📅 <b>Программа:</b> {program_name}"
    )
    
    try:
        await bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML")
        await message.answer(
            "✅ <b>Спасибо!</b> Ваша заявка передана администратору.\n\n"
            "Он свяжется с вами в ближайшее время.\n\n"
            "Можете вернуться к выбору программ:",
            parse_mode="HTML",
            reply_markup=back_to_main_kb
        )
    except Exception as e:
        logging.error(f"Ошибка отправки админу: {e}")
        await message.answer(
            "⚠️ <b>Произошла ошибка</b> при отправке заявки.\n\n"
            "Попробуйте позже или свяжитесь с поддержкой напрямую.\n\n"
            "Вернуться к программам:",
            parse_mode="HTML",
            reply_markup=back_to_main_kb
        )
    
    await state.clear()


# ==================== ЗАПУСК БОТА ====================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    print("🤖 Бот успешно запущен!")
    print(f"📡 @{me.username} готов к работе")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
