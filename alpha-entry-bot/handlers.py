"""
handlers.py - Обработчики команд и кнопок
"""
import time
import asyncio
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_IDS, SUPPORT_URL, t, BOT_NAME
from database import *
from indicators import fetch_price
import httpx

# Состояния пользователей для диалогов
USER_STATES = {}

# ==================== HELPER FUNCTIONS ====================
def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS

async def send_message_safe_local(bot, user_id: int, text: str, **kwargs):
    """Локальная версия для handlers"""
    from aiogram.utils.exceptions import RetryAfter, TelegramAPIError
    try:
        await bot.send_message(user_id, text, **kwargs)
        return True
    except RetryAfter as e:
        await asyncio.sleep(e.timeout)
        return await send_message_safe_local(bot, user_id, text, **kwargs)
    except TelegramAPIError:
        return False

# ==================== KEYBOARDS ====================
def main_menu_kb(is_admin_user: bool, is_paid_user: bool, lang: str = "ru"):
    kb = InlineKeyboardMarkup(row_width=2)
    if is_paid_user:
        kb.add(
            InlineKeyboardButton(t(lang, "btn_alerts"), callback_data="menu_alerts"),
            InlineKeyboardButton(t(lang, "btn_ref"), callback_data="menu_ref")
        )
    kb.add(
        InlineKeyboardButton(t(lang, "btn_guide"), callback_data="menu_guide"),
        InlineKeyboardButton(t(lang, "btn_support"), url=SUPPORT_URL)
    )
    if not is_paid_user:
        kb.add(InlineKeyboardButton(t(lang, "btn_unlock"), callback_data="menu_pay"))
    if is_admin_user:
        kb.add(InlineKeyboardButton(t(lang, "btn_admin"), callback_data="menu_admin"))
    kb.add(InlineKeyboardButton("🌐 Language", callback_data="change_lang"))
    return kb

def alerts_kb(user_pairs: list, lang: str = "ru"):
    from config import DEFAULT_PAIRS
    kb = InlineKeyboardMarkup(row_width=2)
    for pair in DEFAULT_PAIRS:
        emoji = "✅" if pair in user_pairs else "➕"
        kb.add(InlineKeyboardButton(f"{emoji} {pair}", callback_data=f"toggle_{pair}"))
    
    add_btn = "➕ Своя монета" if lang == "ru" else "➕ Custom coin"
    my_btn = "📋 Мои монеты" if lang == "ru" else "📋 My coins"
    info_btn = "💡 Как это работает?" if lang == "ru" else "💡 How it works?"
    
    kb.add(
        InlineKeyboardButton(add_btn, callback_data="add_custom"),
        InlineKeyboardButton(my_btn, callback_data="my_pairs")
    )
    kb.add(InlineKeyboardButton(info_btn, callback_data="alerts_info"))
    kb.add(InlineKeyboardButton(t(lang, "btn_back"), callback_data="back_main"))
    return kb

def ref_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔗 Моя ссылка", callback_data="ref_link"),
        InlineKeyboardButton("💰 Баланс", callback_data="ref_balance")
    )
    kb.add(
        InlineKeyboardButton("💎 Вывод (крипта)", callback_data="ref_withdraw_crypto"),
        InlineKeyboardButton("⭐ Вывод (Stars)", callback_data="ref_withdraw_stars")
    )
    kb.add(InlineKeyboardButton("📖 Гайд для рефов", callback_data="ref_guide"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_main"))
    return kb

def pay_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("⭐ Оплата Stars", callback_data="pay_stars"),
        InlineKeyboardButton("💎 Крипто", callback_data="pay_crypto")
    )
    kb.add(InlineKeyboardButton("🎟 У меня код", callback_data="pay_code"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_main"))
    return kb

def admin_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Статистика", callback_data="adm_stats"),
        InlineKeyboardButton("📢 Рассылка", callback_data="adm_broadcast")
    )
    kb.add(
        InlineKeyboardButton("✅ Выдать доступ", callback_data="adm_grant"),
        InlineKeyboardButton("💰 Начислить", callback_data="adm_give")
    )
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_main"))
    return kb

# ==================== SETUP HANDLERS ====================
def setup_handlers(dp):
    """Регистрация всех хендлеров"""
    
    # ==================== MAIN COMMANDS ====================
    @dp.message_handler(commands=["start"])
    async def cmd_start(message: types.Message):
        uid = message.from_user.id
        args = message.get_args()
        invited_by = int(args) if args and args.isdigit() and int(args) != uid else None
        
        conn = await db_pool.acquire()
        try:
            await conn.execute(
                "INSERT OR IGNORE INTO users(id, invited_by, created_ts) VALUES(?,?,?)",
                (uid, invited_by, int(time.time()))
            )
            await conn.commit()
        finally:
            await db_pool.release(conn)
        
        text = f"<b>🚀 {BOT_NAME}</b>\n\n"
        text += "Точные сигналы с автоматическим TP/SL\n\n"
        text += "• 3-5 сильных сигналов в день\n"
        text += "• Мультистратегия (5+ индикаторов)\n"
        text += "• Объяснение каждого входа\n\n"
        text += "📖 Жми Инструкция для деталей"
        
        paid = await is_paid(uid)
        await message.answer(text, reply_markup=main_menu_kb(is_admin(uid), paid))
    
    # ==================== NAVIGATION ====================
    @dp.callback_query_handler(lambda c: c.data == "back_main")
    async def back_main(call: types.CallbackQuery):
        lang = await get_user_lang(call.from_user.id)
        paid = await is_paid(call.from_user.id)
        try:
            await call.message.edit_text(t(lang, "main_menu"), 
                                         reply_markup=main_menu_kb(is_admin(call.from_user.id), paid, lang))
        except:
            pass
        await call.answer()
    
    # ==================== ALERTS ====================
    @dp.callback_query_handler(lambda c: c.data == "menu_alerts")
    async def menu_alerts(call: types.CallbackQuery):
        uid = call.from_user.id
        lang = await get_user_lang(uid)
        
        if not await is_paid(uid):
            await call.answer(t(lang, "access_required"), show_alert=True)
            return
        
        pairs = await get_user_pairs(uid)
        
        if lang == "ru":
            text = f"📈 <b>Управление алертами</b>\n\nВыбери монеты (до 10)\n\nАктивно: {len(pairs)}/10"
        else:
            text = f"📈 <b>Manage Alerts</b>\n\nSelect coins (up to 10)\n\nActive: {len(pairs)}/10"
        
        await call.message.edit_text(text, reply_markup=alerts_kb(pairs, lang))
        await call.answer()
    
    @dp.callback_query_handler(lambda c: c.data.startswith("toggle_"))
    async def toggle_pair(call: types.CallbackQuery):
        uid = call.from_user.id
        if not await is_paid(uid):
            await call.answer("Оплатите доступ!", show_alert=True)
            return
        
        pair = call.data.split("_", 1)[1]
        pairs = await get_user_pairs(uid)
        
        if pair in pairs:
            await remove_user_pair(uid, pair)
            await call.answer(f"❌ {pair} удалён")
        else:
            if len(pairs) >= 10:
                await call.answer("Максимум 10 монет!", show_alert=True)
                return
            await add_user_pair(uid, pair)
            await call.answer(f"✅ {pair} добавлен")
        
        await menu_alerts(call)
    
    @dp.callback_query_handler(lambda c: c.data == "add_custom")
    async def add_custom(call: types.CallbackQuery):
        uid = call.from_user.id
        pairs = await get_user_pairs(uid)
        if len(pairs) >= 10:
            await call.answer("Максимум 10 монет!", show_alert=True)
            return
        USER_STATES[uid] = {"mode": "waiting_custom_pair"}
        text = "➕ Отправь символ монеты\nПример: <code>SOLUSDT</code>"
        lang = await get_user_lang(uid)
        await call.message.edit_text(text, reply_markup=alerts_kb(pairs, lang))
        await call.answer()
    
    @dp.message_handler(lambda m: USER_STATES.get(m.from_user.id, {}).get("mode") == "waiting_custom_pair")
    async def handle_custom_pair(message: types.Message):
        uid = message.from_user.id
        pair = message.text.strip().upper()
        
        if not pair.endswith("USDT") or len(pair) < 6:
            await message.answer("❌ Неверный формат. Пример: SOLUSDT")
            return
        
        async with httpx.AsyncClient() as client:
            price_data = await fetch_price(client, pair)
            if not price_data:
                await message.answer(f"❌ Пара {pair} не найдена")
                return
        
        await add_user_pair(uid, pair)
        USER_STATES.pop(uid, None)
        await message.answer(f"✅ {pair} добавлена!")
    
    @dp.callback_query_handler(lambda c: c.data == "my_pairs")
    async def my_pairs(call: types.CallbackQuery):
        pairs = await get_user_pairs(call.from_user.id)
        if not pairs:
            await call.answer("Нет активных монет", show_alert=True)
            return
        
        text = "📋 <b>Мои монеты</b>\n\n" + "\n".join(f"• {p}" for p in pairs)
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🗑 Удалить всё", callback_data="clear_all"))
        kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="menu_alerts"))
        await call.message.edit_text(text, reply_markup=kb)
        await call.answer()
    
    @dp.callback_query_handler(lambda c: c.data == "clear_all")
    async def clear_all(call: types.CallbackQuery):
        await clear_user_pairs(call.from_user.id)
        await call.answer("🗑 Всё удалено")
        await menu_alerts(call)
    
    @dp.callback_query_handler(lambda c: c.data == "alerts_info")
    async def alerts_info(call: types.CallbackQuery):
        lang = await get_user_lang(call.from_user.id)
        
        if lang == "ru":
            text = "💡 <b>Как работают алерты?</b>\n\n"
            text += "<b>1. Выбери монеты</b>\nНажми на монету чтобы добавить её в отслеживание.\n\n"
            text += "<b>2. Бот анализирует рынок</b>\n7 индикаторов: EMA, RSI, MACD, BB, Volume, Дивергенции, ATR\n\n"
            text += "<b>3. Получаешь сигнал</b>\nТолько при силе 85+ баллов\n\n"
            text += "<b>4. Управление</b>\n📍 TP1 (15%) - быстрая фиксация\n📍 TP2 (40%) - основная цель\n📍 TP3 (80%) - максимум тренда"
        else:
            text = "💡 <b>How Alerts Work?</b>\n\n"
            text += "<b>1. Select Coins</b>\nClick to add to tracking.\n\n"
            text += "<b>2. Bot Analyzes</b>\n7 indicators: EMA, RSI, MACD, BB, Volume, Divergences, ATR\n\n"
            text += "<b>3. Receive Signal</b>\nOnly when strength 85+ points\n\n"
            text += "<b>4. Management</b>\n📍 TP1 (15%) - quick profit\n📍 TP2 (40%) - main target\n📍 TP3 (80%) - max trend"
        
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(t(lang, "btn_back"), callback_data="menu_alerts"))
        try:
            await call.message.edit_text(text, reply_markup=kb)
        except:
            await call.message.answer(text, reply_markup=kb)
        await call.answer()
    
    # ==================== PAYMENT ====================
    @dp.callback_query_handler(lambda c: c.data == "menu_pay")
    async def menu_pay(call: types.CallbackQuery):
        text = "🔒 <b>Открыть доступ</b>\n\n"
        text += "✅ 3-5 точных сигналов в день\n"
        text += "✅ Автоматический TP/SL\n"
        text += "✅ Мультистратегия\n"
        text += "✅ До 10 монет\n"
        text += "✅ Рефералка 50%"
        await call.message.edit_text(text, reply_markup=pay_kb())
        await call.answer()
    
    @dp.callback_query_handler(lambda c: c.data == "pay_stars")
    async def pay_stars(call: types.CallbackQuery):
        await call.answer("В разработке. Используйте промокод.", show_alert=True)
    
    @dp.callback_query_handler(lambda c: c.data == "pay_crypto")
    async def pay_crypto(call: types.CallbackQuery):
        text = f"💎 <b>Крипто-платёж</b>\n\nНапиши в поддержку для реквизитов.\n\n{SUPPORT_URL}"
        await call.message.edit_text(text, reply_markup=pay_kb())
        await call.answer()
    
    @dp.callback_query_handler(lambda c: c.data == "pay_code")
    async def pay_code(call: types.CallbackQuery):
        USER_STATES[call.from_user.id] = {"mode": "waiting_promo"}
        text = "🎟 Отправь промокод одним сообщением"
        await call.message.edit_text(text, reply_markup=pay_kb())
        await call.answer()
    
    @dp.message_handler(lambda m: USER_STATES.get(m.from_user.id, {}).get("mode") == "waiting_promo")
    async def handle_promo(message: types.Message):
        await grant_access(message.from_user.id)
        USER_STATES.pop(message.from_user.id, None)
        await message.answer("✅ Доступ активирован!\n\nНажми /start")
    
    # ==================== REFERRAL ====================
    @dp.callback_query_handler(lambda c: c.data == "menu_ref")
    async def menu_ref(call: types.CallbackQuery):
        text = "👥 <b>Рефералка</b>\n\n50% от каждой подписки!\nВывод: крипта или Stars\nМинимум: $20"
        await call.message.edit_text(text, reply_markup=ref_kb())
        await call.answer()
    
    @dp.callback_query_handler(lambda c: c.data == "ref_link")
    async def ref_link(call: types.CallbackQuery):
        from aiogram import Bot
        bot = Bot.get_current()
        me = await bot.get_me()
        link = f"https://t.me/{me.username}?start={call.from_user.id}"
        text = f"🔗 <b>Твоя ссылка:</b>\n\n<code>{link}</code>\n\nДелись и зарабатывай 50%!"
        await call.message.edit_text(text, reply_markup=ref_kb(), disable_web_page_preview=True)
        await call.answer()
    
    @dp.callback_query_handler(lambda c: c.data == "ref_balance")
    async def ref_balance_handler(call: types.CallbackQuery):
        balance = await get_user_balance(call.from_user.id)
        refs = await get_user_refs_count(call.from_user.id)
        
        text = f"💰 <b>Баланс</b>\n\nДоступно: ${balance:.2f}\nРефералов: {refs}\n\nМинимум для вывода: $20"
        await call.message.edit_text(text, reply_markup=ref_kb())
        await call.answer()
    
    @dp.callback_query_handler(lambda c: c.data in ["ref_withdraw_crypto", "ref_withdraw_stars"])
    async def ref_withdraw(call: types.CallbackQuery):
        if call.data == "ref_withdraw_crypto":
            text = "💎 <b>Вывод крипты</b>\n\nФормат:\n<code>/withdraw USDT TRC20 адрес сумма</code>"
        else:
            text = "⭐ <b>Вывод Stars</b>\n\nФормат:\n<code>/withdraw_stars сумма</code>"
        await call.message.edit_text(text, reply_markup=ref_kb())
        await call.answer()
    
    @dp.callback_query_handler(lambda c: c.data == "ref_guide")
    async def ref_guide(call: types.CallbackQuery):
        text = "📖 <b>Гайд для партнёров</b>\n\n1. Получи свою ссылку\n2. Делись с друзьями\n3. Получай 50% с подписок\n4. Выводи от $20"
        await call.message.edit_text(text, reply_markup=ref_kb())
        await call.answer()
    
    @dp.message_handler(commands=["withdraw"])
    async def cmd_withdraw(message: types.Message):
        parts = message.text.split()
        if len(parts) != 5:
            await message.reply("❌ Формат: /withdraw USDT TRC20 адрес сумма")
            return
        
        try:
            amount = float(parts[4])
        except:
            await message.reply("❌ Сумма должна быть числом")
            return
        
        if amount < 20:
            await message.reply("❌ Минимум $20")
            return
        
        await message.reply(f"✅ Заявка принята: {amount} {parts[1]}\n\nОжидайте обработки (до 24ч)")
        
        from aiogram import Bot
        bot = Bot.get_current()
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"💸 Вывод\nUser: {message.from_user.id}\n{parts[1]} {parts[2]}\nАдрес: {parts[3]}\nСумма: {amount}"
                )
            except:
                pass
    
    @dp.message_handler(commands=["withdraw_stars"])
    async def cmd_withdraw_stars(message: types.Message):
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply("❌ Формат: /withdraw_stars сумма")
            return
        
        try:
            amount = int(parts[1])
        except:
            await message.reply("❌ Сумма должна быть числом")
            return
        
        if amount < 20:
            await message.reply("❌ Минимум 20 Stars")
            return
        
        await message.reply(f"✅ Заявка на {amount} Stars принята\n\nОжидайте (до 24ч)")
    
    # ==================== GUIDE ====================
    @dp.callback_query_handler(lambda c: c.data == "menu_guide")
    async def menu_guide(call: types.CallbackQuery):
        lang = await get_user_lang(call.from_user.id)
        
        if lang == "ru":
            text = "📖 <b>Инструкция</b>\n\n"
            text += "<b>Шаг 1:</b> Оплати доступ\n"
            text += "<b>Шаг 2:</b> Выбери монеты (до 10)\n"
            text += "<b>Шаг 3:</b> Получай сигналы\n\n"
            text += "<b>В каждом сигнале:</b>\n"
            text += "• Цена входа\n• 🎯 TP1/TP2/TP3\n• 🛡 Stop Loss\n• Причины входа\n• Сила сигнала\n\n"
            text += "<b>⚠️ Важно:</b> Это не финансовый совет"
        else:
            text = "📖 <b>Guide</b>\n\n"
            text += "<b>Step 1:</b> Pay for access\n"
            text += "<b>Step 2:</b> Select coins (up to 10)\n"
            text += "<b>Step 3:</b> Receive signals\n\n"
            text += "<b>Each signal includes:</b>\n"
            text += "• Entry price\n• 🎯 TP1/TP2/TP3\n• 🛡 Stop Loss\n• Entry reasons\n• Signal strength\n\n"
            text += "<b>⚠️ Important:</b> This is not financial advice"
        
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(t(lang, "btn_back"), callback_data="back_main"))
        
        try:
            await call.message.edit_text(text, reply_markup=kb)
        except:
            await call.message.answer(text, reply_markup=kb)
        await call.answer()
    
    # ==================== ADMIN ====================
    @dp.callback_query_handler(lambda c: c.data == "menu_admin")
    async def menu_admin(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            await call.answer("❌ Нет доступа", show_alert=True)
            return
        await call.message.edit_text("👑 <b>Админ-панель</b>", reply_markup=admin_kb())
        await call.answer()
    
    @dp.callback_query_handler(lambda c: c.data == "adm_stats")
    async def adm_stats(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return
        
        total = await get_users_count()
        paid = await get_paid_users_count()
        active = await get_active_users_count()
        
        text = f"📊 <b>Статистика</b>\n\n👥 Всего: {total}\n💎 Оплативших: {paid}\n📈 Активных: {active}"
        await call.message.edit_text(text, reply_markup=admin_kb())
        await call.answer()
    
    @dp.callback_query_handler(lambda c: c.data == "adm_broadcast")
    async def adm_broadcast(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return
        USER_STATES[call.from_user.id] = {"mode": "admin_broadcast"}
        await call.message.edit_text("📢 Отправь текст рассылки", reply_markup=admin_kb())
        await call.answer()
    
    @dp.message_handler(lambda m: USER_STATES.get(m.from_user.id, {}).get("mode") == "admin_broadcast")
    async def handle_broadcast(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        text = message.html_text
        users = await get_all_user_ids()
        
        from aiogram import Bot
        from config import BATCH_SEND_DELAY
        bot = Bot.get_current()
        
        sent = 0
        for user_id in users:
            if await send_message_safe_local(bot, user_id, text, disable_web_page_preview=True):
                sent += 1
            await asyncio.sleep(BATCH_SEND_DELAY)
        
        USER_STATES.pop(message.from_user.id, None)
        await message.reply(f"✅ Разослано: {sent}/{len(users)}")
    
    @dp.callback_query_handler(lambda c: c.data == "adm_grant")
    async def adm_grant(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return
        USER_STATES[call.from_user.id] = {"mode": "admin_grant"}
        await call.message.edit_text("✅ Отправь ID пользователя", reply_markup=admin_kb())
        await call.answer()
    
    @dp.message_handler(lambda m: USER_STATES.get(m.from_user.id, {}).get("mode") == "admin_grant")
    async def handle_grant(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        
        try:
            uid = int(message.text.strip())
        except:
            await message.reply("❌ ID должен быть числом")
            return
        
        await grant_access(uid)
        USER_STATES.pop(message.from_user.id, None)
        await message.reply(f"✅ Доступ выдан: {uid}")
        
        from aiogram import Bot
        bot = Bot.get_current()
        try:
            await bot.send_message(uid, "🎉 Доступ активирован!\n\nНажми /start")
        except:
            pass
    
    @dp.callback_query_handler(lambda c: c.data == "adm_give")
    async def adm_give(call: types.CallbackQuery):
        if not is_admin(call.from_user.id):
            return
        USER_STATES[call.from_user.id] = {"mode": "admin_give_uid"}
        await call.message.edit_text("💰 Отправь ID пользователя", reply_markup=admin_kb())
        await call.answer()
    
    @dp.message_handler(lambda m: USER_STATES.get(m.from_user.id, {}).get("mode") == "admin_give_uid")
    async def handle_give_uid(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        try:
            uid = int(message.text.strip())
        except:
            await message.reply("❌ ID должен быть числом")
            return
        USER_STATES[message.from_user.id] = {"mode": "admin_give_amount", "target_id": uid}
        await message.reply("Отправь сумму")
    
    @dp.message_handler(lambda m: USER_STATES.get(m.from_user.id, {}).get("mode") == "admin_give_amount")
    async def handle_give_amount(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        try:
            amount = float(message.text.strip())
        except:
            await message.reply("❌ Сумма должна быть числом")
            return
        
        uid = USER_STATES[message.from_user.id]["target_id"]
        await add_balance(uid, amount)
        
        USER_STATES.pop(message.from_user.id, None)
        await message.reply(f"✅ Начислено ${amount:.2f} → {uid}")