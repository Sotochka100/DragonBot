import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8708789229:AAHmtDgLGFfA-2RLhRk9IQC876oaE5pdiMw"
OPERATOR_ID = 8590057757

# =================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# ========== КОМАНДЫ ==========
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🛍 Сделать заказ", callback_data="order"),
        types.InlineKeyboardButton("⭐ Отзывы", callback_data="reviews"),
        types.InlineKeyboardButton("📞 Оператор", callback_data="contact"),
        types.InlineKeyboardButton("ℹ️ О нас", callback_data="about")
    )
    await message.answer("🌟 Добро пожаловать!", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'reviews')
async def process_reviews(callback: types.CallbackQuery):
    text = "⭐ *ОТЗЫВЫ*\n\n"
    text += "👤 @crypto_fox ⭐⭐⭐⭐⭐\n"
    text += "🔥 Отличный товар!\n\n"
    text += "👤 @dark_knight ⭐⭐⭐⭐⭐\n"
    text += "💯 Быстрая доставка\n\n"
    text += "👤 @moon_walker ⭐⭐⭐⭐\n"
    text += "👌 Качественно\n\n"
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back"))
    
    await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'back')
async def process_back(callback: types.CallbackQuery):
    await start(callback.message)

@dp.callback_query_handler(lambda c: c.data == 'contact')
async def process_contact(callback: types.CallbackQuery):
    await bot.send_message(OPERATOR_ID, f"👤 @{callback.from_user.username} просит связи")
    await callback.message.edit_text("✅ Запрос отправлен!")

@dp.callback_query_handler(lambda c: c.data == 'about')
async def process_about(callback: types.CallbackQuery):
    text = "ℹ️ *О нас*\n\n✅ Работаем с 2020"
    await callback.message.edit_text(text, parse_mode='Markdown')

@dp.callback_query_handler(lambda c: c.data == 'order')
async def process_order(callback: types.CallbackQuery):
    await callback.message.edit_text("📍 Функция заказа временно отключена")

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("🚀 Бот запущен...")
    executor.start_polling(dp, skip_updates=True)
