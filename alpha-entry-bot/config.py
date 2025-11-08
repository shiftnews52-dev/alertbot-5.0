"""
config.py - Все настройки и константы бота (УЛУЧШЕННАЯ ВЕРСИЯ С ТАЙМФРЕЙМАМИ)
"""
import os

# ==================== BOT SETTINGS ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("BOT_NAME", "Alpha Entry Bot")
SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/support")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()}
DB_PATH = os.getenv("DB_PATH", "bot.db")

# ==================== TRADING SETTINGS ====================
# Дефолтные монеты
DEFAULT_PAIRS = ["BTCUSDT", "ETHUSDT", "TONUSDT"]

# ==================== ТАЙМФРЕЙМЫ ====================
# Выбери один из вариантов:
# "1h"  - 1 час (рекомендуется для начала)
# "4h"  - 4 часа (меньше сигналов, но качественнее)
# "1d"  - 1 день (самые надежные сигналы)
# "15m" - 15 минут (для дейтрейдинга)
# "1m"  - 1 минута (много шума, не рекомендуется)

TIMEFRAME = os.getenv("TIMEFRAME", "1h")  # По умолчанию 1 час

# Преобразование таймфрейма в секунды
TIMEFRAME_MAP = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
}

CANDLE_TF = TIMEFRAME_MAP.get(TIMEFRAME, 3600)  # По умолчанию 1 час

# Интервалы проверок (зависят от таймфрейма)
if CANDLE_TF <= 900:  # До 15 минут
    CHECK_INTERVAL = 60  # Проверять каждую минуту
elif CANDLE_TF <= 3600:  # До 1 часа
    CHECK_INTERVAL = 300  # Проверять каждые 5 минут
else:  # 4h и больше
    CHECK_INTERVAL = 900  # Проверять каждые 15 минут

MAX_CANDLES = 300  # Максимум свечей в истории

# ==================== INDICATORS ====================
EMA_FAST = 9
EMA_SLOW = 21
EMA_TREND = 50
EMA_LONG_TREND = 200

RSI_PERIOD = 14
RSI_OVERSOLD = 35
RSI_OVERBOUGHT = 65

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

BB_PERIOD = 20
BB_STD = 2

# ==================== FILTERS ====================
MIN_SIGNAL_SCORE = 70      # Оптимальное значение (было 85)
MAX_SIGNALS_PER_DAY = 5    # Максимум сигналов в день
SIGNAL_COOLDOWN = CANDLE_TF * 6  # 6 свечей между сигналами одной пары

# ==================== OPTIMIZATION ====================
PRICE_CACHE_TTL = 30       # Кэш цен на 30 секунд
BATCH_SEND_SIZE = 30       # Отправлять группами по 30
BATCH_SEND_DELAY = 0.05    # Задержка между сообщениями

# ==================== IMAGES ====================
IMG_START = os.getenv("IMG_START", "")
IMG_ALERTS = os.getenv("IMG_ALERTS", "")
IMG_REF = os.getenv("IMG_REF", "")
IMG_PAYWALL = os.getenv("IMG_PAYWALL", "")
IMG_GUIDE = os.getenv("IMG_GUIDE", "")

# ==================== TRANSLATIONS ====================
TEXTS = {
    "ru": {
        # Общие
        "welcome": "Выбери язык / Choose language",
        "main_menu": "Главное меню",
        "back": "⬅️ Назад",
        
        # Стартовое сообщение
        "start_text": f"<b>🚀 {BOT_NAME}</b>\n\nТочные сигналы с автоматическим TP/SL\nТаймфрейм: {TIMEFRAME}\n\n• 3-5 сильных сигналов в день\n• Мультистратегия (5+ индикаторов)\n• Объяснение каждого входа\n\n📖 Жми Инструкция для деталей",
        
        # Кнопки главного меню
        "btn_alerts": "📈 Алерты",
        "btn_ref": "👥 Рефералка",
        "btn_guide": "📖 Инструкция",
        "btn_support": "💬 Поддержка",
        "btn_unlock": "🔓 Открыть доступ",
        "btn_admin": "👑 Админ",
        "btn_back": "⬅️ Назад",
        
        # Алерты
        "alerts_title": "📈 <b>Управление алертами</b>\n\nВыбери монеты (до 10)\n\nАктивно: {count}/10",
        "add_custom_coin": "➕ Своя монета",
        "my_coins": "📋 Мои монеты",
        "how_it_works": "💡 Как это работует?",
        "access_required": "Оплатите доступ для использования алертов!",
        "coin_removed": "❌ {pair} удалён",
        "coin_added": "✅ {pair} добавлен",
        "max_coins": "Максимум 10 монет!",
        "no_active_coins": "Нет активных монет",
        "all_removed": "🗑 Всё удалено",
        "send_coin_symbol": "➕ Отправь символ монеты\nПример: <code>SOLUSDT</code>",
        "invalid_format": "❌ Неверный формат. Пример: SOLUSDT",
        "pair_not_found": "❌ Пара {pair} не найдена",
        
        # Инструкция
        "guide_title": "📖 <b>Инструкция</b>",
        "guide_step1": "<b>Шаг 1:</b> Оплати доступ",
        "guide_step2": "<b>Шаг 2:</b> Выбери монеты (до 10)",
        "guide_step3": "<b>Шаг 3:</b> Получай сигналы",
        "guide_signal_info": "<b>В каждом сигнале:</b>\n• Цена входа\n• 🎯 TP1/TP2/TP3\n• 🛡 Stop Loss\n• Причины входа\n• Сила сигнала",
        "guide_disclaimer": "<b>⚠️ Важно:</b> Это не финансовый совет",
        
        # Оплата
        "payment_title": "🔓 <b>Открыть доступ</b>",
        "payment_features": "✅ 3-5 точных сигналов в день\n✅ Автоматический TP/SL\n✅ Мультистратегия\n✅ До 10 монет\n✅ Рефералка 50%",
        "pay_stars": "⭐ Оплата Stars",
        "pay_crypto": "💎 Крипто",
        "pay_code": "🎟 У меня код",
        "send_promo": "🎟 Отправь промокод одним сообщением",
        "access_granted": "✅ Доступ активирован!\n\nНажми /start",
        "in_development": "В разработке. Используйте промокод.",
        "crypto_payment_info": "💎 <b>Крипто-платёж</b>\n\nНапиши в поддержку для реквизитов.\n\n{support_url}",
        
        # Реферальная программа
        "ref_title": "👥 <b>Рефералка</b>\n\n50% от каждой подписки!\nВывод: крипта или Stars\nМинимум: $20",
        "ref_link": "🔗 <b>Твоя ссылка:</b>\n\n<code>{link}</code>\n\nДелись и зарабатывай 50%!",
        "ref_balance": "💰 <b>Баланс</b>\n\nДоступно: ${balance:.2f}\nРефералов: {refs}\n\nМинимум для вывода: $20",
        "ref_guide_text": "📖 <b>Гайд для партнёров</b>\n\n1. Получи свою ссылку\n2. Делись с друзьями\n3. Получай 50% с подписок\n4. Выводи от $20",
        "withdraw_crypto_format": "💎 <b>Вывод крипты</b>\n\nФормат:\n<code>/withdraw USDT TRC20 адрес сумма</code>",
        "withdraw_stars_format": "⭐ <b>Вывод Stars</b>\n\nФормат:\n<code>/withdraw_stars сумма</code>",
        "withdraw_invalid_format": "❌ Формат: /withdraw USDT TRC20 адрес сумма",
        "withdraw_invalid_amount": "❌ Сумма должна быть числом",
        "withdraw_min_amount": "❌ Минимум $20",
        "withdraw_accepted": "✅ Заявка принята: {amount} {currency}\n\nОжидайте обработки (до 24ч)",
        
        # Админ панель
        "admin_title": "👑 <b>Админ-панель</b>",
        "admin_stats": "📊 <b>Статистика</b>\n\n👥 Всего: {total}\n💎 Оплативших: {paid}\n📈 Активных: {active}",
        "admin_send_broadcast": "📢 Отправь текст рассылки",
        "admin_send_user_id": "✅ Отправь ID пользователя",
        "admin_send_amount": "Отправь сумму",
        "admin_invalid_id": "❌ ID должен быть числом",
        "admin_access_granted": "✅ Доступ выдан: {uid}",
        "admin_balance_added": "✅ Начислено ${amount:.2f} → {uid}",
        "admin_broadcast_done": "✅ Разослано: {sent}/{total}",
        "admin_no_access": "❌ Нет доступа",
        
        # Язык
        "language_select": "🌐 <b>Выбери язык</b>",
        "language_changed": "✅ Язык изменён на Русский",
    },
    "en": {
        # General
        "welcome": "Выбери язык / Choose language",
        "main_menu": "Main Menu",
        "back": "⬅️ Back",
        
        # Start message
        "start_text": f"<b>🚀 {BOT_NAME}</b>\n\nAccurate signals with automatic TP/SL\nTimeframe: {TIMEFRAME}\n\n• 3-5 strong signals per day\n• Multi-strategy (5+ indicators)\n• Explanation for each entry\n\n📖 Press Guide for details",
        
        # Main menu buttons
        "btn_alerts": "📈 Alerts",
        "btn_ref": "👥 Referrals",
        "btn_guide": "📖 Guide",
        "btn_support": "💬 Support",
        "btn_unlock": "🔓 Unlock Access",
        "btn_admin": "👑 Admin",
        "btn_back": "⬅️ Back",
        
        # Alerts
        "alerts_title": "📈 <b>Manage Alerts</b>\n\nSelect coins (up to 10)\n\nActive: {count}/10",
        "add_custom_coin": "➕ Custom coin",
        "my_coins": "📋 My coins",
        "how_it_works": "💡 How it works?",
        "access_required": "Please pay for access to use alerts!",
        "coin_removed": "❌ {pair} removed",
        "coin_added": "✅ {pair} added",
        "max_coins": "Maximum 10 coins!",
        "no_active_coins": "No active coins",
        "all_removed": "🗑 All removed",
        "send_coin_symbol": "➕ Send coin symbol\nExample: <code>SOLUSDT</code>",
        "invalid_format": "❌ Invalid format. Example: SOLUSDT",
        "pair_not_found": "❌ Pair {pair} not found",
        
        # Guide
        "guide_title": "📖 <b>Guide</b>",
        "guide_step1": "<b>Step 1:</b> Pay for access",
        "guide_step2": "<b>Step 2:</b> Select coins (up to 10)",
        "guide_step3": "<b>Step 3:</b> Receive signals",
        "guide_signal_info": "<b>Each signal includes:</b>\n• Entry price\n• 🎯 TP1/TP2/TP3\n• 🛡 Stop Loss\n• Entry reasons\n• Signal strength",
        "guide_disclaimer": "<b>⚠️ Important:</b> This is not financial advice",
        
        # Payment
        "payment_title": "🔓 <b>Unlock Access</b>",
        "payment_features": "✅ 3-5 accurate signals per day\n✅ Automatic TP/SL\n✅ Multi-strategy\n✅ Up to 10 coins\n✅ 50% referral program",
        "pay_stars": "⭐ Pay with Stars",
        "pay_crypto": "💎 Crypto",
        "pay_code": "🎟 I have a code",
        "send_promo": "🎟 Send promo code in one message",
        "access_granted": "✅ Access activated!\n\nPress /start",
        "in_development": "In development. Use promo code.",
        "crypto_payment_info": "💎 <b>Crypto Payment</b>\n\nContact support for payment details.\n\n{support_url}",
        
        # Referral program
        "ref_title": "👥 <b>Referral Program</b>\n\n50% from each subscription!\nWithdrawal: crypto or Stars\nMinimum: $20",
        "ref_link": "🔗 <b>Your link:</b>\n\n<code>{link}</code>\n\nShare and earn 50%!",
        "ref_balance": "💰 <b>Balance</b>\n\nAvailable: ${balance:.2f}\nReferrals: {refs}\n\nMinimum withdrawal: $20",
        "ref_guide_text": "📖 <b>Partner Guide</b>\n\n1. Get your link\n2. Share with friends\n3. Earn 50% from subscriptions\n4. Withdraw from $20",
        "withdraw_crypto_format": "💎 <b>Crypto Withdrawal</b>\n\nFormat:\n<code>/withdraw USDT TRC20 address amount</code>",
        "withdraw_stars_format": "⭐ <b>Stars Withdrawal</b>\n\nFormat:\n<code>/withdraw_stars amount</code>",
        "withdraw_invalid_format": "❌ Format: /withdraw USDT TRC20 address amount",
        "withdraw_invalid_amount": "❌ Amount must be a number",
        "withdraw_min_amount": "❌ Minimum $20",
        "withdraw_accepted": "✅ Request accepted: {amount} {currency}\n\nProcessing (up to 24h)",
        
        # Admin panel
        "admin_title": "👑 <b>Admin Panel</b>",
        "admin_stats": "📊 <b>Statistics</b>\n\n👥 Total: {total}\n💎 Paid: {paid}\n📈 Active: {active}",
        "admin_send_broadcast": "📢 Send broadcast message",
        "admin_send_user_id": "✅ Send user ID",
        "admin_send_amount": "Send amount",
        "admin_invalid_id": "❌ ID must be a number",
        "admin_access_granted": "✅ Access granted: {uid}",
        "admin_balance_added": "✅ Added ${amount:.2f} → {uid}",
        "admin_broadcast_done": "✅ Sent: {sent}/{total}",
        "admin_no_access": "❌ No access",
        
        # Language
        "language_select": "🌐 <b>Choose Language</b>",
        "language_changed": "✅ Language changed to English",
    }
}

def t(uid_or_lang, key: str, **kwargs) -> str:
    """Получить перевод с поддержкой форматирования"""
    if isinstance(uid_or_lang, str):
        lang = uid_or_lang
    else:
        lang = "ru"
    
    text = TEXTS.get(lang, TEXTS["ru"]).get(key, key)
    
    # Форматирование если есть kwargs
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    
    return text

# Информация о текущих настройках
print("=" * 60)
print(f"📊 НАСТРОЙКИ ТАЙМФРЕЙМА")
print("=" * 60)
print(f"Таймфрейм: {TIMEFRAME}")
print(f"Секунд в свече: {CANDLE_TF}")
print(f"Интервал проверки: {CHECK_INTERVAL}s")
print(f"Cooldown: {SIGNAL_COOLDOWN}s ({SIGNAL_COOLDOWN/3600:.1f}ч)")
print(f"Минимальный score: {MIN_SIGNAL_SCORE}")
print("=" * 60)
