#!/bin/bash
# Alpha Entry Bot - Quick Start Script

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Alpha Entry Bot - Quick Start"
echo "================================"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 не установлен${NC}"
    echo "Установите Python 3.8+: https://www.python.org/downloads/"
    exit 1
fi

echo -e "${GREEN}✅ Python найден:${NC} $(python3 --version)"

# Проверка .env файла
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Файл .env не найден${NC}"
    echo "Создаём .env из примера..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}📝 Отредактируй .env и добавь BOT_TOKEN и ADMIN_IDS${NC}"
        exit 1
    else
        echo -e "${RED}❌ Файл .env.example не найден${NC}"
        exit 1
    fi
fi

# Проверка переменных
source .env

if [ -z "$BOT_TOKEN" ]; then
    echo -e "${RED}❌ BOT_TOKEN не указан в .env${NC}"
    exit 1
fi

if [ -z "$ADMIN_IDS" ]; then
    echo -e "${RED}❌ ADMIN_IDS не указан в .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Конфигурация найдена${NC}"

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo "📦 Создаём виртуальное окружение..."
    python3 -m venv venv
fi

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
echo "📦 Устанавливаем зависимости..."
pip install -q -r requirements.txt

echo -e "${GREEN}✅ Зависимости установлены${NC}"

# Экспорт переменных
export BOT_TOKEN
export ADMIN_IDS
export SUPPORT_URL
export BOT_NAME

# Запуск бота
echo ""
echo -e "${GREEN}🤖 Запускаем бота...${NC}"
echo -e "${YELLOW}Нажми Ctrl+C для остановки${NC}"
echo ""

python3 main.py