#!/usr/bin/env python3
"""
check_render.py - Проверка готовности к деплою на Render
Запуск: python check_render.py
"""
import os
import sys

def check_python_version():
    """Проверить версию Python"""
    print("🐍 Проверка версии Python...")
    version = sys.version_info
    
    if version.major == 3 and version.minor == 11:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    elif version.major == 3 and version.minor >= 8:
        print(f"  ⚠️  Python {version.major}.{version.minor}.{version.micro} (рекомендуется 3.11.9)")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (нужна минимум 3.8)")
        return False

def check_file(filename, required=True):
    """Проверить наличие файла"""
    if os.path.exists(filename):
        print(f"✅ {filename} найден")
        return True
    else:
        status = "❌" if required else "⚠️ "
        print(f"{status} {filename} {'отсутствует' if required else 'отсутствует (опционально)'}")
        return not required

def check_requirements():
    """Проверить requirements.txt"""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt не найден")
        return False
    
    with open("requirements.txt") as f:
        content = f.read()
        required = ["aiogram", "aiosqlite", "httpx"]
        
        for pkg in required:
            if pkg in content:
                print(f"  ✅ {pkg} указан")
            else:
                print(f"  ❌ {pkg} отсутствует")
                return False
    
    return True

def check_env_example():
    """Проверить .env.example"""
    if not os.path.exists(".env.example"):
        print("⚠️  .env.example не найден")
        return True
    
    with open(".env.example") as f:
        content = f.read()
        required = ["BOT_TOKEN", "ADMIN_IDS"]
        
        for var in required:
            if var in content:
                print(f"  ✅ {var} в примере")
            else:
                print(f"  ⚠️  {var} не в примере")
    
    return True

def check_gitignore():
    """Проверить .gitignore"""
    if not os.path.exists(".gitignore"):
        print("⚠️  .gitignore не найден - создай его!")
        return False
    
    with open(".gitignore") as f:
        content = f.read()
        important = [".env", "*.db"]
        
        for item in important:
            if item in content:
                print(f"  ✅ {item} исключён")
            else:
                print(f"  ❌ {item} НЕ исключён (опасность утечки секретов!)")
                return False
    
    return True

def check_secrets():
    """Проверить что секреты не в коде"""
    files_to_check = ["main.py", "config.py", "handlers.py"]
    
    dangerous_patterns = [
        ("bot_token =", "хардкод токена"),
        ("BOT_TOKEN =", "хардкод токена"),
        ("admin_ids =", "хардкод админов"),
    ]
    
    found_issues = False
    
    for filename in files_to_check:
        if not os.path.exists(filename):
            continue
        
        with open(filename) as f:
            content = f.read().lower()
            
            for pattern, description in dangerous_patterns:
                if pattern.lower() in content and "os.getenv" not in content[max(0, content.find(pattern.lower())-50):content.find(pattern.lower())+50]:
                    print(f"  ⚠️  Возможен {description} в {filename}")
                    found_issues = True
    
    if not found_issues:
        print(f"  ✅ Секреты не захардкожены")
    
    return not found_issues

def main():
    print("=" * 60)
    print("🔍 Проверка готовности к деплою на Render")
    print("=" * 60)
    print()
    
    checks = []
    
    # Версия Python
    checks.append(check_python_version())
    print()
    
    # Основные файлы
    print("📁 Проверка основных файлов...")
    checks.append(check_file("main.py"))
    checks.append(check_file("config.py"))
    checks.append(check_file("database.py"))
    checks.append(check_file("indicators.py"))
    checks.append(check_file("handlers.py"))
    checks.append(check_file("tasks.py"))
    print()
    
    # Конфигурация
    print("⚙️  Проверка конфигурации...")
    checks.append(check_file("requirements.txt"))
    checks.append(check_file("runtime.txt", required=False))
    checks.append(check_file("render.yaml", required=False))
    print()
    
    # Requirements
    print("📦 Проверка зависимостей...")
    checks.append(check_requirements())
    print()
    
    # .env.example
    print("🔐 Проверка примера настроек...")
    checks.append(check_env_example())
    print()
    
    # .gitignore
    print("🚫 Проверка .gitignore...")
    checks.append(check_gitignore())
    print()
    
    # Секреты
    print("🔒 Проверка безопасности...")
    checks.append(check_secrets())
    print()
    
    # Результат
    print("=" * 60)
    if all(checks):
        print("✅ ВСЁ ГОТОВО К ДЕПЛОЮ НА RENDER!")
        print()
        print("Следующие шаги:")
        print("1. git add . && git commit -m 'Ready for Render'")
        print("2. git push origin main")
        print("3. Создай Web Service на render.com")
        print("4. Добавь переменные BOT_TOKEN и ADMIN_IDS")
        print("5. Жди ~2 минуты и всё готово!")
        print()
        print("📖 Подробная инструкция: RENDER_DEPLOY.md")
        sys.exit(0)
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ - ИСПРАВЬ ИХ ПЕРЕД ДЕПЛОЕМ")
        print()
        print("💡 Прочитай инструкцию: RENDER_DEPLOY.md")
        sys.exit(1)

if __name__ == "__main__":
    main()