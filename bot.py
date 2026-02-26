import asyncio
import logging
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import string

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8708789229:AAHmtDgLGFfA-2RLhRk9IQC876oaE5pdiMw"
OPERATOR_ID = 8590057757

# ТВОИ КОШЕЛЬКИ
USDT_ADDRESS = "TS9LHAdZotW4G89WGUyv1xqsBFzQU5NFwv"
BTC_ADDRESS = "bc1q78uuqujyshxams6v5me2lfwp0pnyaxn5cff9xt"

# Курсы
USDT_RUB = 90
BTC_RUB = 4500000

# =================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ========== СОСТОЯНИЯ ==========
class OrderStates(StatesGroup):
    main_menu = State()
    choosing_city = State()
    choosing_product = State()
    choosing_weight = State()
    choosing_currency = State()
    waiting_for_payment = State()
    order_confirmed = State()
    viewing_orders = State()
    viewing_reviews = State()
    writing_review = State()
    choosing_review_rating = State()
    viewing_reviews_page = State()

# ========== ДАННЫЕ ==========
CITIES = ["Челябинск", "Миасс", "Златоуст", "Екатеринбург", "Пермь", "Копейск", "Куса"]

PRODUCTS = {
    "product1": "Мефедрон(Мяу)",
    "product2": "Героин(Гера)", 
    "product3": "Alpha-PVP(Соль)"
}

WEIGHTS = ["0.5 грамм", "1 грамм", "1.5 грамма", "2 грамма"]

PRICES_RUB = {
    ("product1", "0.5 грамм"): 1000,
    ("product1", "1 грамм"): 1800,
    ("product1", "1.5 грамма"): 2500,
    ("product1", "2 грамма"): 3200,
    ("product2", "0.5 грамм"): 1200,
    ("product2", "1 грамм"): 2000,
    ("product2", "1.5 грамма"): 2800,
    ("product2", "2 грамма"): 3600,
    ("product3", "0.5 грамм"): 1500,
    ("product3", "1 грамм"): 2500,
    ("product3", "1.5 грамма"): 3400,
    ("product3", "2 грамма"): 4300,
}

# Хранилище
orders = {}
user_orders = {}
reviews = []  # Для хранения отзывов

# ========== РЕАЛЬНЫЕ ЮЗЕРНЕЙМЫ ==========
REAL_USERNAMES = [
    "@crypto_fox", "@dark_knight_88", "@moon_walker_23", "@btc_maxi_2017", "@eth_king_2021",
    "@solana_cowboy", "@ton_keeper_2024", "@bnb_lord_2022", "@trust_user_777", "@metamask_king",
    "@coinbase_pro", "@binance_queen", "@bybit_trader", "@alex_chelyabinsk", "@dmitry_miass",
    "@max_ekb_96", "@artem_zlatoust", "@vlad_perm_59", "@kate_crypto_88", "@anna_trade_99",
    "@siberian_king", "@ural_steel", "@altay_mountain", "@baikal_water", "@kamchatka_fire",
    "@python_dev", "@js_wizard", "@rust_ace", "@go_lang_master", "@swift_dev"
]

# ========== ТЕКСТЫ ОТЗЫВОВ ==========
REVIEW_TEXTS = [
    "🔥 Товар просто огонь! Брал уже 3 раза, всегда качественно",
    "💯 Все пришло быстро, упаковано отлично. Рекомендую!",
    "👌 Хороший продукт, соответствует описанию",
    "✨ Очень доволен покупкой, буду заказывать еще",
    "⚡️ Быстрая доставка, вежливый оператор",
    "💰 Лучшее соотношение цены и качества",
    "🎁 Приятный бонус при заказе, спасибо!",
    "📦 Упаковка супер, ничего не повредилось",
    "🤝 Продавец всегда на связи, отвечает быстро",
    "💫 Товар порадовал, буду советовать друзьям",
    "🔝 Один из лучших продавцов в этом городе",
    "✅ Все честно, без обмана. Проверено",
    "🚀 Доставка быстрее чем ожидал",
    "💎 Качество на высоте, спасибо большое",
    "🌿 Очень мягкий и приятный эффект",
    "💪 Товар мощный, рекомендую кто шарит",
    "🤫 Все анонимно и безопасно",
    "🔒 Приватность соблюдена, спасибо",
    "📱 Удобно заказывать через бота",
    "🧪 Качество лабораторное, проверял"
]

# ========== ГЕНЕРАЦИЯ ОТЗЫВОВ ==========
def generate_reviews():
    all_reviews = []
    
    # Генерируем 400 отзывов с РЕАЛЬНЫМИ юзерами
    for i in range(400):
        rating = random.choices([5, 4, 3], weights=[80, 15, 5])[0]
        review = {
            'id': len(all_reviews) + 1,
            'username': random.choice(REAL_USERNAMES),
            'rating': rating,
            'text': random.choice(REVIEW_TEXTS),
            'date': f"{random.randint(1,28):02d}.{random.randint(1,12):02d}.2024",
            'likes': random.randint(5, 150),
            'dislikes': random.randint(0, 15)
        }
        all_reviews.append(review)
    
    # Генерируем 238 отзывов с обычными юзерами
    for i in range(238):
        rating = random.choices([5, 4, 3], weights=[70, 20, 10])[0]
        review = {
            'id': len(all_reviews) + 1,
            'username': f"@user_{random.randint(10000, 99999)}",
            'rating': rating,
            'text': random.choice(REVIEW_TEXTS),
            'date': f"{random.randint(1,28):02d}.{random.randint(1,12):02d}.2024",
            'likes': random.randint(0, 50),
            'dislikes': random.randint(0, 10)
        }
        all_reviews.append(review)
    
    # Перемешиваем
    random.shuffle(all_reviews)
    
    # Добавляем несколько отзывов с 3 звездами для реалистичности
    for i in range(5):
        all_reviews.append({
            'id': len(all_reviews) + 1,
            'username': random.choice(REAL_USERNAMES),
            'rating': 3,
            'text': random.choice(["Нормальный товар, но можно и лучше", "В целом ок, но доставка подвела", "Хорошо, но цена кусается"]),
            'date': f"{random.randint(1,28):02d}.{random.randint(1,12):02d}.2024",
            'likes': random.randint(0, 20),
            'dislikes': random.randint(0, 30)
        })
    
    return all_reviews

reviews = generate_reviews()

def generate_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ========== КЛАВИАТУРЫ ==========
def main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 Сделать заказ", callback_data="make_order")
    builder.button(text="📋 Мои заказы", callback_data="my_orders")
    builder.button(text="⭐ Отзывы", callback_data="view_reviews_0")
    builder.button(text="📞 Связаться с оператором", callback_data="contact_operator")
    builder.button(text="ℹ️ О нас", callback_data="about_us")
    builder.adjust(1)
    return builder.as_markup()

def cities_menu():
    builder = InlineKeyboardBuilder()
    for city in CITIES:
        builder.button(text=city, callback_data=f"city_{city}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_main"))
    return builder.as_markup()

def products_menu():
    builder = InlineKeyboardBuilder()
    for pid, name in PRODUCTS.items():
        builder.button(text=name, callback_data=f"product_{pid}")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="◀️ Назад к городам", callback_data="back_to_cities"))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main"))
    return builder.as_markup()

def weights_menu(pid):
    builder = InlineKeyboardBuilder()
    for w in WEIGHTS:
        price_rub = PRICES_RUB.get((pid, w), 0)
        price_usdt = round(price_rub / USDT_RUB, 2)
        price_btc = round(price_rub / BTC_RUB, 8)
        builder.button(
            text=f"{w} | {price_rub} руб / {price_usdt} USDT / {price_btc} BTC", 
            callback_data=f"weight_{pid}_{w}"
        )
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="◀️ Назад к товарам", callback_data="back_to_products"))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main"))
    return builder.as_markup()

def currency_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 USDT (TRC-20)", callback_data="pay_usdt")
    builder.button(text="₿ Bitcoin", callback_data="pay_btc")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="◀️ Назад к весу", callback_data="back_to_weights"))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main"))
    return builder.as_markup()

def order_confirmed_menu(order_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Мой заказ", callback_data=f"view_order_{order_id}")
    builder.button(text="📞 Связаться с оператором", callback_data="contact_operator")
    builder.button(text="🛍 Новый заказ", callback_data="make_order")
    builder.button(text="🏠 Главное меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def reviews_keyboard(page=0):
    builder = InlineKeyboardBuilder()
    
    # Кнопка "Написать отзыв"
    builder.button(text="✍️ Написать отзыв", callback_data="write_review")
    
    # Навигация
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Предыдущие", callback_data=f"view_reviews_{page-1}"))
    if (page + 1) * 5 < len(reviews):
        nav_row.append(InlineKeyboardButton(text="Следующие ▶️", callback_data=f"view_reviews_{page+1}"))
    
    if nav_row:
        builder.row(*nav_row)
    
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main"))
    return builder.as_markup()

def rating_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(5, 0, -1):
        builder.button(text="⭐" * i, callback_data=f"rate_{i}")
    builder.row(InlineKeyboardButton(text="◀️ Отмена", callback_data="view_reviews_0"))
    return builder.as_markup()

# ========== СТАРТ ==========
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("🌟 *Добро пожаловать!*\n\n🔮 Более 600 довольных клиентов\n\nВыбери действие:", 
                        parse_mode='Markdown', 
                        reply_markup=main_menu())
    await state.set_state(OrderStates.main_menu)

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🌟 *Главное меню*", 
                                    parse_mode='Markdown', 
                                    reply_markup=main_menu())
    await state.set_state(OrderStates.main_menu)
    await callback.answer()

# ========== ОТЗЫВЫ ==========
@dp.callback_query(F.data.startswith("view_reviews_"))
async def view_reviews(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[2])
    start_idx = page * 5
    end_idx = start_idx + 5
    page_reviews = reviews[start_idx:end_idx]
    
    # Статистика
    total = len(reviews)
    avg_rating = sum(r['rating'] for r in reviews) / total
    five_star = sum(1 for r in reviews if r['rating'] == 5)
    four_star = sum(1 for r in reviews if r['rating'] == 4)
    three_star = sum(1 for r in reviews if r['rating'] == 3)
    
    text = f"⭐ *ОТЗЫВЫ* (стр. {page+1}/{(total-1)//5+1})\n"
    text += f"📊 Всего: {total} | Рейтинг: {avg_rating:.2f}\n"
    text += f"5⭐:{five_star} 4⭐:{four_star} 3⭐:{three_star}\n"
    text += "━━━━━━━━━━━━━━━━\n\n"
    
    for review in page_reviews:
        stars = "⭐" * review['rating']
        text += f"👤 {review['username']} {stars}\n"
        text += f"💬 {review['text']}\n"
        text += f"📅 {review['date']} | 👍 {review['likes']}\n"
        text += "━━━━━━━━━━━━━━━━\n\n"
    
    await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=reviews_keyboard(page))
    await state.set_state(OrderStates.viewing_reviews)
    await callback.answer()

# ========== НАПИСАТЬ ОТЗЫВ ==========
@dp.callback_query(F.data == "write_review")
async def write_review(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✍️ *НАПИСАТЬ ОТЗЫВ*\n\n"
        "Напиши текст своего отзыва одним сообщением.\n\n"
        "Например: *Отличный товар, всё супер!*",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardBuilder().button(text="◀️ Отмена", callback_data="view_reviews_0").as_markup()
    )
    await state.set_state(OrderStates.writing_review)
    await callback.answer()

@dp.message(OrderStates.writing_review)
async def review_text_received(message: types.Message, state: FSMContext):
    await state.update_data(review_text=message.text)
    await message.answer(
        "⭐ *ОЦЕНИ ТОВАР*\n\nВыбери количество звезд:",
        parse_mode='Markdown',
        reply_markup=rating_keyboard()
    )
    await state.set_state(OrderStates.choosing_review_rating)

@dp.callback_query(F.data.startswith("rate_"))
async def review_rating_chosen(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])
    data = await state.get_data()
    review_text = data.get('review_text', '')
    
    # Добавляем отзыв
    new_review = {
        'id': len(reviews) + 1,
        'username': f"@{callback.from_user.username or f'user_{callback.from_user.id}'}",
        'rating': rating,
        'text': review_text,
        'date': datetime.now().strftime("%d.%m.%Y"),
        'likes': 0,
        'dislikes': 0
    }
    reviews.append(new_review)
    
    await callback.message.edit_text(
        f"✅ *СПАСИБО ЗА ОТЗЫВ!*\n\n"
        f"Оценка: {'⭐' * rating}\n"
        f"Отзыв: {review_text}\n\n"
        f"Он появится в общем списке.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardBuilder().button(text="◀️ К отзывам", callback_data="view_reviews_0").as_markup()
    )
    await state.set_state(OrderStates.main_menu)
    await callback.answer()

# ========== ЗАКАЗ ==========
@dp.callback_query(F.data == "make_order")
async def make_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📍 *Выбери город:*", parse_mode='Markdown', reply_markup=cities_menu())
    await state.set_state(OrderStates.choosing_city)
    await callback.answer()

@dp.callback_query(F.data.startswith("city_"))
async def city_chosen(callback: CallbackQuery, state: FSMContext):
    city = callback.data.split("_")[1]
    await state.update_data(city=city)
    await callback.message.edit_text(f"✅ *Город:* {city}\n\n📦 *Выбери товар:*", parse_mode='Markdown', reply_markup=products_menu())
    await state.set_state(OrderStates.choosing_product)
    await callback.answer()

@dp.callback_query(F.data == "back_to_cities")
async def back_to_cities(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📍 *Выбери город:*", parse_mode='Markdown', reply_markup=cities_menu())
    await state.set_state(OrderStates.choosing_city)
    await callback.answer()

@dp.callback_query(F.data.startswith("product_"))
async def product_chosen(callback: CallbackQuery, state: FSMContext):
    pid = callback.data.split("_")[1]
    await state.update_data(product=pid)
    await callback.message.edit_text(f"✅ *{PRODUCTS[pid]}*\n\n⚖️ *Выбери вес:*", parse_mode='Markdown', reply_markup=weights_menu(pid))
    await state.set_state(OrderStates.choosing_weight)
    await callback.answer()

@dp.callback_query(F.data == "back_to_products")
async def back_to_products(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📦 *Выбери товар:*", parse_mode='Markdown', reply_markup=products_menu())
    await state.set_state(OrderStates.choosing_product)
    await callback.answer()

@dp.callback_query(F.data.startswith("weight_"))
async def weight_chosen(callback: CallbackQuery, state: FSMContext):
    _, pid, weight = callback.data.split("_", 2)
    price_rub = PRICES_RUB.get((pid, weight), 0)
    await state.update_data(weight=weight, price_rub=price_rub)
    await callback.message.edit_text(f"💰 *Сумма:* {price_rub} руб\n\n💳 *Выбери способ оплаты:*", parse_mode='Markdown', reply_markup=currency_menu())
    await state.set_state(OrderStates.choosing_currency)
    await callback.answer()

@dp.callback_query(F.data == "back_to_weights")
async def back_to_weights(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text("⚖️ *Выбери вес:*", parse_mode='Markdown', reply_markup=weights_menu(data['product']))
    await state.set_state(OrderStates.choosing_weight)
    await callback.answer()

# ========== ОПЛАТА ==========
@dp.callback_query(F.data == "pay_usdt")
async def pay_usdt(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    price_rub = data['price_rub']
    order_id = generate_order_id()
    usdt_amount = round(price_rub / USDT_RUB, 2)
    
    orders[order_id] = {
        'user_id': callback.from_user.id,
        'username': callback.from_user.username,
        'city': data['city'],
        'product': PRODUCTS[data['product']],
        'weight': data['weight'],
        'amount_rub': price_rub,
        'amount_crypto': usdt_amount,
        'currency': 'USDT',
        'status': 'pending',
        'time': datetime.now().strftime("%d.%m.%Y %H:%M")
    }
    
    user_id = callback.from_user.id
    if user_id not in user_orders:
        user_orders[user_id] = []
    if order_id not in user_orders[user_id]:
        user_orders[user_id].insert(0, order_id)
    
    trust_link = f"https://link.trustwallet.com/send?asset=c20000714_tTR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t&address={USDT_ADDRESS}&amount={usdt_amount}&memo={order_id}"
    
    text = (
        f"🧾 *ЗАКАЗ #{order_id}*\n\n"
        f"🏙 *Город:* {data['city']}\n"
        f"📦 *Товар:* {PRODUCTS[data['product']]}\n"
        f"⚖️ *Вес:* {data['weight']}\n"
        f"💰 *Сумма:* {price_rub} руб | {usdt_amount} USDT\n\n"
        f"📬 *Адрес:* `{USDT_ADDRESS}`\n"
        f"📝 *Комментарий:* `{order_id}`"
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔗 ОТКРЫТЬ TRUST WALLET", url=trust_link)
    kb.button(text="✅ Я ОПЛАТИЛ", callback_data=f"confirm_{order_id}")
    kb.button(text="◀️ Назад", callback_data="back_to_currency")
    kb.button(text="🏠 Главное меню", callback_data="back_to_main")
    kb.adjust(1)
    
    await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=kb.as_markup())
    await state.update_data(order_id=order_id)
    await state.set_state(OrderStates.waiting_for_payment)
    await callback.answer()

@dp.callback_query(F.data == "pay_btc")
async def pay_btc(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    price_rub = data['price_rub']
    order_id = generate_order_id()
    btc_amount = round(price_rub / BTC_RUB, 8)
    
    orders[order_id] = {
        'user_id': callback.from_user.id,
        'username': callback.from_user.username,
        'city': data['city'],
        'product': PRODUCTS[data['product']],
        'weight': data['weight'],
        'amount_rub': price_rub,
        'amount_crypto': btc_amount,
        'currency': 'BTC',
        'status': 'pending',
        'time': datetime.now().strftime("%d.%m.%Y %H:%M")
    }
    
    user_id = callback.from_user.id
    if user_id not in user_orders:
        user_orders[user_id] = []
    if order_id not in user_orders[user_id]:
        user_orders[user_id].insert(0, order_id)
    
    trust_link = f"https://link.trustwallet.com/send?asset=bitcoin&address={BTC_ADDRESS}&amount={btc_amount}&memo={order_id}"
    
    text = (
        f"🧾 *ЗАКАЗ #{order_id}*\n\n"
        f"🏙 *Город:* {data['city']}\n"
        f"📦 *Товар:* {PRODUCTS[data['product']]}\n"
        f"⚖️ *Вес:* {data['weight']}\n"
        f"💰 *Сумма:* {price_rub} руб | {btc_amount} BTC\n\n"
        f"📬 *Адрес:* `{BTC_ADDRESS}`\n"
        f"📝 *Комментарий:* `{order_id}`"
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔗 ОТКРЫТЬ TRUST WALLET", url=trust_link)
    kb.button(text="✅ Я ОПЛАТИЛ", callback_data=f"confirm_{order_id}")
    kb.button(text="◀️ Назад", callback_data="back_to_currency")
    kb.button(text="🏠 Главное меню", callback_data="back_to_main")
    kb.adjust(1)
    
    await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=kb.as_markup())
    await state.update_data(order_id=order_id)
    await state.set_state(OrderStates.waiting_for_payment)
    await callback.answer()

# ========== ПОДТВЕРЖДЕНИЕ ОПЛАТЫ ==========
@dp.callback_query(F.data.startswith("confirm_"))
async def confirm_payment(callback: CallbackQuery, state: FSMContext):
    order_id = callback.data.split("_")[1]
    order = orders.get(order_id, {})
    
    if order_id in orders:
        orders[order_id]['status'] = 'paid'
    
    await bot.send_message(
        OPERATOR_ID, 
        f"🆕 *НОВЫЙ ЗАКАЗ*\n🧾 {order_id}\n👤 @{callback.from_user.username}\n💰 {order.get('amount_rub', 0)} руб",
        parse_mode='Markdown'
    )
    
    await callback.message.edit_text(
        f"✅ *ЗАКАЗ #{order_id} ПОДТВЕРЖДЕН!*\n\nСпасибо! Оператор свяжется с тобой.",
        parse_mode='Markdown',
        reply_markup=order_confirmed_menu(order_id)
    )
    
    await state.set_state(OrderStates.order_confirmed)
    await callback.answer()

# ========== МОИ ЗАКАЗЫ ==========
@dp.callback_query(F.data == "my_orders")
async def my_orders(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_order_list = user_orders.get(user_id, [])
    
    if not user_order_list:
        await callback.message.edit_text(
            "📋 *У вас пока нет заказов*",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
    else:
        text = "📋 *Ваши заказы:*\n\n"
        for order_id in user_order_list[:5]:
            order = orders.get(order_id, {})
            status = "✅" if order.get('status') == 'paid' else "⏳"
            text += f"{status} `{order_id}` - {order.get('product', '')}\n"
        
        await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=main_menu())
    
    await state.set_state(OrderStates.viewing_orders)
    await callback.answer()

@dp.callback_query(F.data.startswith("view_order_"))
async def view_order(callback: CallbackQuery, state: FSMContext):
    order_id = callback.data.split("_")[2]
    order = orders.get(order_id, {})
    
    text = (
        f"📋 *ЗАКАЗ #{order_id}*\n\n"
        f"🏙 Город: {order.get('city', '')}\n"
        f"📦 Товар: {order.get('product', '')}\n"
        f"⚖️ Вес: {order.get('weight', '')}\n"
        f"💰 Сумма: {order.get('amount_rub', 0)} руб\n"
        f"✅ Статус: {'Оплачен' if order.get('status') == 'paid' else 'Ожидает'}"
    )
    
    await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=main_menu())
    await callback.answer()

# ========== СВЯЗЬ С ОПЕРАТОРОМ ==========
@dp.callback_query(F.data == "contact_operator")
async def contact_operator(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(OPERATOR_ID, f"📞 *Запрос связи*\n👤 @{callback.from_user.username}", parse_mode='Markdown')
    await callback.message.edit_text("✅ Запрос отправлен!", reply_markup=main_menu())
    await callback.answer()

# ========== О НАС ==========
@dp.callback_query(F.data == "about_us")
async def about_us(callback: CallbackQuery, state: FSMContext):
    text = (
        "ℹ️ *О нас*\n\n"
        "✅ Работаем с 2024 года\n"
        "✅ Только качественные товары\n"
        "✅ Быстрая доставка\n"
        "✅ Анонимно и безопасно\n"
        "✅ Более 600 довольных клиентов"
        "❌Отзывы временно не реботают"
    )
    await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=main_menu())
    await callback.answer()

# ========== ЗАПУСК ==========
async def main():
    print("🚀 Бот с отзывами запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())