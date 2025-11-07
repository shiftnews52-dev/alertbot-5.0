#!/usr/bin/env python3
"""
import_history_tf.py - Импорт исторических данных с поддержкой таймфреймов
Использование: 
    python import_history_tf.py BTCUSDT 1h 300
    python import_history_tf.py ETHUSDT 4h 200
    python import_history_tf.py TONUSDT 1d 100
"""
import sys
import asyncio
import httpx
import time
from indicators import CANDLES
from config import CANDLE_TF, TIMEFRAME

# Маппинг таймфреймов для Binance API
BINANCE_INTERVALS = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
}

async def import_history(pair: str, timeframe: str, count: int = 300):
    """Импортировать историю с Binance для указанного таймфрейма"""
    print(f"📥 Импорт {count} свечей для {pair} на таймфрейме {timeframe}...")
    
    if timeframe not in BINANCE_INTERVALS:
        print(f"  ❌ Неподдерживаемый таймфрейм: {timeframe}")
        print(f"     Доступные: {', '.join(BINANCE_INTERVALS.keys())}")
        return False
    
    async with httpx.AsyncClient() as client:
        try:
            # Binance Klines API
            url = "https://api.binance.com/api/v3/klines"
            params = {
                "symbol": pair.upper(),
                "interval": BINANCE_INTERVALS[timeframe],
                "limit": min(count, 1000)  # Binance лимит
            }
            
            print(f"  🔗 Запрос к Binance API...")
            resp = await client.get(url, params=params, timeout=10.0)
            resp.raise_for_status()
            
            klines = resp.json()
            print(f"  ✅ Получено {len(klines)} свечей ({timeframe})")
            
            # Очищаем старые данные
            CANDLES.candles[pair.upper()].clear()
            
            # Добавляем в хранилище
            added = 0
            for kline in klines:
                open_time = kline[0] / 1000  # ms -> s
                open_price = float(kline[1])
                high_price = float(kline[2])
                low_price = float(kline[3])
                close_price = float(kline[4])
                volume = float(kline[5])
                
                # Рассчитываем bucket на основе таймфрейма
                tf_seconds = {
                    "1m": 60, "5m": 300, "15m": 900, "30m": 1800,
                    "1h": 3600, "4h": 14400, "1d": 86400
                }[timeframe]
                
                bucket = int(open_time // tf_seconds) * tf_seconds
                
                candle = {
                    "ts": bucket,
                    "o": open_price,
                    "h": high_price,
                    "l": low_price,
                    "c": close_price,
                    "v": volume
                }
                
                CANDLES.candles[pair.upper()].append(candle)
                added += 1
            
            print(f"  ✅ Добавлено {added} свечей в хранилище")
            
            # Проверка
            total = len(CANDLES.get_candles(pair))
            print(f"  📊 Всего свечей для {pair}: {total}")
            
            if total >= 250:
                print(f"  ✅ Достаточно данных для анализа!")
            else:
                print(f"  ⚠️ Нужно ещё {250 - total} свечей")
            
            # Статистика
            closes = [c["c"] for c in CANDLES.get_candles(pair)]
            if closes:
                print(f"  📈 Диапазон цен: {min(closes):.2f} - {max(closes):.2f}")
                print(f"  📊 Текущая цена: {closes[-1]:.2f}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            return False

async def import_all_default(timeframe: str, count: int = 300):
    """Импортировать все дефолтные пары"""
    from config import DEFAULT_PAIRS
    
    print("=" * 60)
    print(f"📥 МАССОВЫЙ ИМПОРТ ({timeframe})")
    print("=" * 60)
    print()
    
    for pair in DEFAULT_PAIRS:
        success = await import_history(pair, timeframe, count)
        if not success:
            print(f"  ⚠️ Пропускаем {pair}")
        print()
        await asyncio.sleep(0.5)  # Небольшая задержка между запросами
    
    print("=" * 60)
    print("✅ МАССОВЫЙ ИМПОРТ ЗАВЕРШЁН!")
    print("=" * 60)

async def main():
    if len(sys.argv) < 2:
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║          ИМПОРТ ИСТОРИЧЕСКИХ ДАННЫХ С ТАЙМФРЕЙМАМИ          ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        print("📋 Использование:")
        print()
        print("  1️⃣ Импорт одной пары:")
        print("     python import_history_tf.py BTCUSDT 1h 300")
        print("     python import_history_tf.py ETHUSDT 4h 200")
        print("     python import_history_tf.py TONUSDT 1d 100")
        print()
        print("  2️⃣ Импорт всех дефолтных пар:")
        print("     python import_history_tf.py all 1h 300")
        print("     python import_history_tf.py all 4h 200")
        print()
        print("📊 Доступные таймфреймы:")
        print("     1m, 5m, 15m, 30m, 1h, 4h, 1d")
        print()
        print("💡 Рекомендации:")
        print("     • 1h  - 300 свечей (12.5 дней)")
        print("     • 4h  - 250 свечей (41 день)")
        print("     • 1d  - 250 свечей (8 месяцев)")
        print()
        print(f"🔧 Текущий таймфрейм в config.py: {TIMEFRAME}")
        print()
        sys.exit(1)
    
    pair = sys.argv[1].upper()
    timeframe = sys.argv[2] if len(sys.argv) > 2 else TIMEFRAME
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    
    print("=" * 60)
    print("📥 ИМПОРТ ИСТОРИЧЕСКИХ ДАННЫХ")
    print("=" * 60)
    print()
    
    if pair == "ALL":
        await import_all_default(timeframe, count)
    else:
        success = await import_history(pair, timeframe, count)
        
        if success:
            print()
            print("=" * 60)
            print("✅ ИМПОРТ ЗАВЕРШЁН!")
            print("=" * 60)
            print()
            print("💡 Теперь можно:")
            print("   1. Запустить бота: python main.py")
            print("   2. Или протестировать: python debug_signals.py")
            print()
            print("⚙️  Убедись что в config.py:")
            print(f"   TIMEFRAME = '{timeframe}'")
        else:
            print()
            print("❌ Импорт не удался")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
