"""
config.py - Все настройки и константы бота
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

# Интервалы проверок
CHECK_INTERVAL = 60  # 1 минута между проверками
CANDLE_TF = 60       # Таймфрейм свечи в секундах
MAX_CANDLES = 300    # Максимум свечей в истории

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
MIN_SIGNAL_SCORE = 85      # Минимальная сила сигнала
MAX_SIGNALS_PER_DAY = 3    # Максимум сигналов в день
SIGNAL_COOLDOWN = 21600    # 6 часов между сигналами одной пары

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
        "welcome": "Выбери язык / Choose language",
        "main_menu": "Главное меню",
        "start_text": f"<b>🚀 {BOT_NAME}</b>\n\nТочные сигналы с автоматическим TP/SL\n\n• 3 сигнала в день (только сильные)\n• Мультистратегия (7 индикаторов)\n• 3 уровня Take Profit\n• Объяснение каждого входа\n\n📖 Жми Инструкция",
        "btn_alerts": "📈 Алерты",
        "btn_ref": "👥 Рефералка",
        "btn_guide": "📖 Инструкция",
        "btn_support": "💬 Поддержка",
        "btn_unlock": "🔓 Открыть доступ",
        "btn_admin": "👑 Админ",
        "btn_back": "⬅️ Назад",
        "access_required": "Оплатите доступ для использования алертов!",
    },
    "en": {
        "welcome": "Выбери язык / Choose language",
        "main_menu": "Main Menu",
        "start_text": f"<b>🚀 {BOT_NAME}</b>\n\nAccurate signals with automatic TP/SL\n\n• 3 signals per day (only strong)\n• Multi-strategy (7 indicators)\n• 3 Take Profit levels\n• Explanation for each entry\n\n📖 Press Guide",
        "btn_alerts": "📈 Alerts",
        "btn_ref": "👥 Referrals",
        "btn_guide": "📖 Guide",
        "btn_support": "💬 Support",
        "btn_unlock": "🔓 Unlock Access",
        "btn_admin": "👑 Admin",
        "btn_back": "⬅️ Back",
        "access_required": "Please pay for access to use alerts!",
    }
}

def t(uid_or_lang, key: str) -> str:
    """Получить перевод"""
    if isinstance(uid_or_lang, str):
        lang = uid_or_lang
    else:
        lang = "ru"
    return TEXTS.get(lang, TEXTS["ru"]).get(key, key)