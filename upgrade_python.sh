#!/bin/bash
# Скрипт обновления до Python 3.11.9

set -e  # Остановка при ошибке

echo "🐍 Обновление до Python 3.11.9"
echo "================================"
echo

# Проверка текущей версии
echo "📊 Текущая версия Python:"
python3 --version || python --version
echo

# Определение ОС
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Linux detected"
    
    # Ubuntu/Debian
    if command -v apt &> /dev/null; then
        echo "📦 Установка Python 3.11 через apt..."
        sudo apt update
        sudo apt install -y python3.11 python3.11-venv python3.11-dev
    
    # Fedora/RHEL
    elif command -v dnf &> /dev/null; then
        echo "📦 Установка Python 3.11 через dnf..."
        sudo dnf install -y python3.11
    
    else
        echo "⚠️  Неизвестный дистрибутив Linux"
        echo "Установи Python 3.11 вручную: https://www.python.org/downloads/"
        exit 1
    fi

elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS detected"
    
    if command -v brew &> /dev/null; then
        echo "📦 Установка Python 3.11 через Homebrew..."
        brew install python@3.11
    else
        echo "❌ Homebrew не установлен"
        echo "Установи Homebrew: https://brew.sh"
        exit 1
    fi

else
    echo "❓ Неизвестная ОС: $OSTYPE"
    echo "Установи Python 3.11.9 вручную: https://www.python.org/downloads/"
    exit 1
fi

echo
echo "✅ Python 3.11 установлен!"
python3.11 --version
echo

# Создание нового виртуального окружения
if [ -d "venv" ]; then
    echo "🗑️  Удаление старого виртуального окружения..."
    rm -rf venv
fi

echo "📦 Создание нового виртуального окружения с Python 3.11..."
python3.11 -m venv venv

echo "🔌 Активация виртуального окружения..."
source venv/bin/activate

echo "📥 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

echo
echo "✅ Обновление завершено!"
echo
echo "📋 Проверка:"
python --version
echo

echo "🧪 Запуск тестов..."
if python test_indicators.py; then
    echo
    echo "🎉 Всё работает отлично с Python 3.11.9!"
    echo
    echo "📝 Следующие шаги:"
    echo "1. Проверь что бот работает: python main.py"
    echo "2. Закоммить изменения: git add ."
    echo "3. git commit -m 'Upgrade to Python 3.11.9'"
    echo "4. git push"
else
    echo
    echo "❌ Тесты провалились. Проверь ошибки выше."
    exit 1
fi