#!/bin/bash
# Alpha Entry Bot - Start script for Render
# С автоматическим импортом исторических данных

set -e  # Остановка при ошибке

echo "============================================================"
echo "🚀 Alpha Entry Bot - Starting on Render"
echo "============================================================"
echo ""

# ==================== ПРОВЕРКИ ====================
echo "🔍 Pre-flight checks..."
echo ""

# Python версия
echo "🐍 Python version:"
python --version
echo ""

# Переменные окружения
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ ERROR: BOT_TOKEN not set!"
    echo "   Go to Render Dashboard → Environment → Add BOT_TOKEN"
    exit 1
fi

if [ -z "$ADMIN_IDS" ]; then
    echo "❌ ERROR: ADMIN_IDS not set!"
    echo "   Go to Render Dashboard → Environment → Add ADMIN_IDS"
    exit 1
fi

echo "✅ BOT_TOKEN: Set"
echo "✅ ADMIN_IDS: Set"

# Таймфрейм (по умолчанию 1h)
TIMEFRAME=${TIMEFRAME:-1h}
echo "✅ TIMEFRAME: ${TIMEFRAME}"
echo ""

# ==================== ИМПОРТ ИСТОРИИ ====================
echo "============================================================"
echo "📥 Importing historical data (${TIMEFRAME} timeframe)"
echo "============================================================"
echo ""

# Проверяем наличие скрипта
if [ -f "import_history_tf.py" ]; then
    echo "📊 Importing 300 candles for default pairs..."
    
    # Импорт с обработкой ошибок
    if python import_history_tf.py all ${TIMEFRAME} 300; then
        echo ""
        echo "✅ Historical data imported successfully!"
    else
        echo ""
        echo "⚠️  Warning: Import failed, but continuing..."
        echo "   Bot will work but needs time to collect data"
        echo "   (~4 hours for 1h timeframe)"
    fi
else
    echo "⚠️  Warning: import_history_tf.py not found"
    echo "   Bot will start but needs time to collect data"
fi

echo ""

# ==================== ЗАПУСК БОТА ====================
echo "============================================================"
echo "🤖 Starting main bot..."
echo "============================================================"
echo ""

# Экспорт переменных (на случай если нужно)
export BOT_TOKEN
export ADMIN_IDS
export TIMEFRAME
export SUPPORT_URL=${SUPPORT_URL:-https://t.me/support}
export BOT_NAME=${BOT_NAME:-Alpha Entry Bot}

# Запуск
python main.py
