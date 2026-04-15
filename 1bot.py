import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime, timedelta

# ===== НАСТРОЙКИ =====
TOKEN = "8617615907:AAEvE6tQZLwbd-Mmz_pPu2soVXpwD_crG4o"  # ВСТАВЬ СВОЙ ТОКЕН
ADMIN_ID = 854447207  # ТВОЙ TELEGRAM ID

# Словарь пользователей: {user_id: дата_окончания}
USERS_ACCESS = {}

# Доступ даётся на 7 дней (изменено с 30 на 7)
DEFAULT_ACCESS_DAYS = 7

# Хранилище заявок
PENDING_REQUESTS = {}

# Программы
PROGRAMS = {
    "recovery": {
        "name": "Восстановление",
        "description": "Мягкая практика для восстановления после нагрузок."
    },
    "resource": {
        "name": "Ресурсный код",
        "description": "Практика для наполнения энергией и внутренним ресурсом."
    },
    "harmony": {
        "name": "Гармония движения",
        "description": "Плавные движения для баланса тела и ума."
    },
    "express": {
        "name": "Экспресс-обновление",
        "description": "Быстрая практика для бодрости и ясности."
    },
     "floating": {
        "name": "Нейрофлоатинг",
        "description": "Авторская практика ментора проекта Михаила Бирюкова для снятия глубокого физического и эмоционального напряжения."
    }
}

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== ПРОВЕРКА ДОСТУПА =====
def is_user_allowed(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    if user_id not in USERS_ACCESS:
        return False
    expiry_date = USERS_ACCESS[user_id]
    if expiry_date > datetime.now():
        return True
    else:
        del USERS_ACCESS[user_id]
        return False

def request_access_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Подать заявку на доступ", callback_data="request_access")]
    ])

def main_menu():
    buttons = []
    for key, prog in PROGRAMS.items():
        buttons.append([InlineKeyboardButton(text=prog["name"], callback_data=key)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ===== MIDDLEWARE =====
class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        if hasattr(event, 'from_user'):
            user = event.from_user
        elif hasattr(event, 'message') and event.message:
            user = event.message.from_user
        elif hasattr(event, 'callback_query') and event.callback_query:
            user = event.callback_query.from_user
        
        if user:
            user_id = user.id
            
            if user_id == ADMIN_ID:
                return await handler(event, data)
            
            is_auth_command = False
            if hasattr(event, 'message') and event.message:
                text = event.message.text or ""
                if text.startswith('/start') or text.startswith('/status') or text.startswith('/expiry'):
                    is_auth_command = True
            if hasattr(event, 'callback_query') and event.callback_query:
                if event.callback_query.data in ["request_access", "menu"]:
                    is_auth_command = True
            
            if not is_user_allowed(user_id) and not is_auth_command:
                if hasattr(event, 'message') and event.message:
                    await event.message.answer(
                        "🚫 Доступ запрещён\n\n"
                        "Нажмите кнопку ниже, чтобы отправить заявку администратору.",
                        reply_markup=request_access_keyboard()
                    )
                elif hasattr(event, 'callback_query') and event.callback_query:
                    if event.callback_query.message:
                        await event.callback_query.message.answer(
                            "🚫 Доступ запрещён\n\n"
                            "Нажмите кнопку ниже, чтобы отправить заявку администратору.",
                            reply_markup=request_access_keyboard()
                        )
                    await event.callback_query.answer()
                return
        
        return await handler(event, data)

# ===== КОМАНДА /start =====
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    
    if is_user_allowed(user_id):
        await message.answer(
            "🌟 Добро пожаловать!\n\nВыберите программу:",
            reply_markup=main_menu()
        )
    else:
        await message.answer(
            "🌟 Добро пожаловать!\n\n"
            "Этот бот содержит закрытый контент.\n"
            "Чтобы получить доступ, нажмите кнопку ниже и дождитесь одобрения администратора.",
            reply_markup=request_access_keyboard()
        )

# ===== ОТПРАВКА ЗАЯВКИ =====
@dp.callback_query(lambda c: c.data == "request_access")
async def request_access(callback: types.CallbackQuery):
    await callback.answer()
    
    user_id = callback.from_user.id
    username = callback.from_user.username or "нет username"
    full_name = callback.from_user.full_name
    
    if is_user_allowed(user_id):
        await callback.message.answer("✅ У вас уже есть доступ! Выберите программу:", reply_markup=main_menu())
        return
    
    PENDING_REQUESTS[user_id] = {
        "username": username,
        "full_name": full_name,
        "user_id": user_id
    }
    
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"deny_{user_id}")
        ]
    ])
    
    await bot.send_message(
        ADMIN_ID,
        f"📝 Новая заявка на доступ!\n\n"
        f"👤 Имя: {full_name}\n"
        f"🆔 Username: @{username}\n"
        f"📱 ID: {user_id}",
        reply_markup=admin_keyboard
    )
    
    await callback.message.answer(
        "✅ Заявка отправлена!\n\n"
        "Администратор рассмотрит ваш запрос в ближайшее время.\n"
        "После одобрения вы получите уведомление."
    )

# ===== ОБРАБОТКА РЕШЕНИЯ АДМИНИСТРАТОРА (кнопки) =====
@dp.callback_query(lambda c: c.data.startswith("approve_") or c.data.startswith("deny_"))
async def handle_admin_decision(callback: types.CallbackQuery):
    await callback.answer()
    
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ У вас нет прав.", show_alert=True)
        return
    
    action, user_id_str = callback.data.split("_")
    user_id = int(user_id_str)
    
    if action == "approve":
        expiry_date = datetime.now() + timedelta(days=DEFAULT_ACCESS_DAYS)
        USERS_ACCESS[user_id] = expiry_date
        
        user_info = PENDING_REQUESTS.pop(user_id, {"full_name": "Пользователь"})
        
        await callback.message.edit_text(
            f"✅ Пользователь {user_info['full_name']} добавлен!"
        )
        
        try:
            await bot.send_message(
                user_id,
                f"🎉 Доступ одобрен!\n\n"
                f"Доступ активен до {expiry_date.strftime('%d.%m.%Y')}.\n"
                f"Нажмите /start, чтобы начать."
            )
        except Exception as e:
            await callback.message.answer(f"⚠️ Не удалось отправить сообщение: {e}")
        
        await callback.answer("✅ Одобрено")
        
    elif action == "deny":
        user_info = PENDING_REQUESTS.pop(user_id, {"full_name": "Пользователь"})
        
        await callback.message.edit_text(
            f"❌ Заявка от {user_info['full_name']} отклонена"
        )
        
        try:
            await bot.send_message(
                user_id,
                "😔 Доступ отклонён\n\nАдминистратор отклонил вашу заявку."
            )
        except Exception:
            pass
        
        await callback.answer("❌ Отклонён")

# ===== КОМАНДА АДМИНИСТРАТОРА: /adduser =====
@dp.message(Command("adduser"))
async def add_user_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет прав.")
        return
    
    parts = message.text.split()
    
    if len(parts) not in [2, 3]:
        await message.answer(
            "❌ Неправильный формат.\n\n"
            "Используйте:\n"
            "/adduser 123456789 — добавить на 7 дней\n"
            "/adduser 123456789 14 — добавить на 14 дней"
        )
        return
    
    try:
        user_id = int(parts[1])
        days = int(parts[2]) if len(parts) == 3 else DEFAULT_ACCESS_DAYS
    except ValueError:
        await message.answer("❌ ID и количество дней должны быть числами.")
        return
    
    expiry_date = datetime.now() + timedelta(days=days)
    USERS_ACCESS[user_id] = expiry_date
    
    await message.answer(
        f"✅ Пользователь {user_id} добавлен!\n"
        f"📅 Доступ до: {expiry_date.strftime('%d.%m.%Y')} (на {days} дней)"
    )
    
    try:
        await bot.send_message(
            user_id,
            f"🎉 Вам открыт доступ к боту!\n\n"
            f"Доступ активен до {expiry_date.strftime('%d.%m.%Y')}.\n"
            f"Нажмите /start, чтобы начать."
        )
    except Exception:
        pass

# ===== КОМАНДА АДМИНИСТРАТОРА: список пользователей =====
@dp.message(Command("users"))
async def list_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет прав.")
        return
    
    if not USERS_ACCESS:
        await message.answer("📋 Список пользователей пуст.")
        return
    
    users_list = []
    for uid, expiry_date in USERS_ACCESS.items():
        if expiry_date > datetime.now():
            days_left = (expiry_date - datetime.now()).days
            status = f"✅ до {expiry_date.strftime('%d.%m.%Y')} (осталось {days_left} дн.)"
        else:
            status = "❌ истёк"
        users_list.append(f"• {uid} — {status}")
    
    await message.answer("👥 Пользователи с доступом:\n\n" + "\n".join(users_list))

# ===== КОМАНДА ДЛЯ ПОЛЬЗОВАТЕЛЯ: узнать срок доступа =====
@dp.message(Command("expiry"))
async def check_expiry(message: types.Message):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        await message.answer("👑 Вы администратор, доступ всегда есть.")
        return
    
    if user_id not in USERS_ACCESS:
        await message.answer("⏳ У вас нет активного доступа.")
        return
    
    expiry_date = USERS_ACCESS[user_id]
    if expiry_date > datetime.now():
        days_left = (expiry_date - datetime.now()).days
        await message.answer(
            f"✅ Доступ активен до: {expiry_date.strftime('%d.%m.%Y')}\n"
            f"📆 Осталось дней: {days_left}"
        )
    else:
        await message.answer("❌ Срок доступа истёк.")

# ===== КОМАНДА ДЛЯ ПРОВЕРКИ СТАТУСА =====
@dp.message(Command("status"))
async def check_status(message: types.Message):
    user_id = message.from_user.id
    if is_user_allowed(user_id):
        await message.answer("✅ У вас есть доступ к боту!")
    else:
        await message.answer("⏳ У вас пока нет доступа.")

# ===== ОБРАБОТКА ВЫБОРА ПРОГРАММЫ =====
@dp.callback_query()
async def handle_choice(callback: types.CallbackQuery):
    if not is_user_allowed(callback.from_user.id):
        await callback.answer("⛔ У вас нет доступа.", show_alert=True)
        return
    
    if callback.data == "menu":
        await callback.message.answer("Главное меню:", reply_markup=main_menu())
        await callback.answer()
        return
    
    prog = PROGRAMS.get(callback.data)
    if prog:
        await callback.message.answer(
            f"📋 {prog['name']}\n\n{prog['description']}\n\n(Видео и аудио будут добавлены позже)"
        )
        back_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В главное меню", callback_data="menu")]
        ])
        await callback.message.answer("Что дальше?", reply_markup=back_btn)
    await callback.answer()

# ===== ЗАПУСК =====
dp.update.middleware(AccessMiddleware())

async def main():
    print("✅ Бот запущен!")
    print(f"👑 Администратор: {ADMIN_ID}")
    print(f"📅 Доступ по умолчанию: {DEFAULT_ACCESS_DAYS} дней")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
