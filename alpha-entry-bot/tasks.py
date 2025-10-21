"""
tasks.py - Фоновые задачи (сбор цен, анализ, рассылка)
"""
import time
import asyncio
import logging
from collections import defaultdict
import httpx
from aiogram import Bot
from aiogram.utils.exceptions import RetryAfter, TelegramAPIError

from config import (
    CHECK_INTERVAL, DEFAULT_PAIRS, 
    MAX_SIGNALS_PER_DAY, SIGNAL_COOLDOWN,
    BATCH_SEND_SIZE, BATCH_SEND_DELAY
)
from database import (
    get_all_tracked_pairs, get_pairs_with_users,
    count_signals_today, log_signal
)
from indicators import (
    CANDLES, PRICE_CACHE, fetch_price, analyze_signal
)

logger = logging.getLogger(__name__)

# Глобальный словарь для cooldown сигналов
LAST_SIGNALS = {}

# ==================== HELPER FUNCTIONS ====================
async def send_message_safe(bot: Bot, user_id: int, text: str, **kwargs):
    """Безопасная отправка с обработкой rate limit"""
    try:
        await bot.send_message(user_id, text, **kwargs)
        return True
    except RetryAfter as e:
        await asyncio.sleep(e.timeout)
        return await send_message_safe(bot, user_id, text, **kwargs)
    except TelegramAPIError:
        return False

# ==================== TASKS ====================
async def price_collector(bot: Bot):
    """Сбор цен с Binance"""
    logger.info("Price collector started")
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Получаем все отслеживаемые пары
                pairs = await get_all_tracked_pairs()
                pairs = list(set(pairs + DEFAULT_PAIRS))
                
                # Собираем цены
                ts = time.time()
                for pair in pairs:
                    price_data = await fetch_price(client, pair)
                    if price_data:
                        price, volume = price_data
                        CANDLES.add_price(pair, price, volume, ts)
                
                # Очистка старого кэша
                PRICE_CACHE.clear_old()
                
            except Exception as e:
                logger.error(f"Price collector error: {e}")
            
            await asyncio.sleep(CHECK_INTERVAL)

async def signal_analyzer(bot: Bot):
    """Анализ и отправка сигналов"""
    logger.info("Signal analyzer started")
    
    while True:
        try:
            # Получаем пары и пользователей
            rows = await get_pairs_with_users()
            
            # Группируем по парам
            pairs_users = defaultdict(list)
            for row in rows:
                pairs_users[row["pair"]].append(row["user_id"])
            
            # Анализируем каждую пару
            now = time.time()
            for pair, users in pairs_users.items():
                # Проверка лимита сигналов за день
                signals_today = await count_signals_today(pair)
                if signals_today >= MAX_SIGNALS_PER_DAY:
                    continue
                
                signal = analyze_signal(pair)
                if not signal:
                    continue
                
                side = signal["side"]
                key = (pair, side)
                
                # Проверка cooldown
                if now - LAST_SIGNALS.get(key, 0) < SIGNAL_COOLDOWN:
                    continue
                
                # Формируем сообщение
                emoji = "📈" if side == "LONG" else "📉"
                text = f"{emoji} <b>СИГНАЛ</b> ({signal['score']}/100)\n\n"
                text += f"<b>Монета:</b> {pair}\n"
                text += f"<b>Вход:</b> {side} @ <code>{signal['price']:.8f}</code>\n\n"
                
                # 3 уровня Take Profit
                text += f"🎯 <b>TP1:</b> <code>{signal['take_profit_1']:.8f}</code> (+{signal['tp1_percent']:.2f}%) [15% позиции]\n"
                text += f"🎯 <b>TP2:</b> <code>{signal['take_profit_2']:.8f}</code> (+{signal['tp2_percent']:.2f}%) [40% позиции]\n"
                text += f"🎯 <b>TP3:</b> <code>{signal['take_profit_3']:.8f}</code> (+{signal['tp3_percent']:.2f}%) [80% позиции]\n\n"
                
                text += f"🛡 <b>SL:</b> <code>{signal['stop_loss']:.8f}</code> (-{signal['sl_percent']:.2f}%)\n\n"
                text += "<b>💡 Причины:</b>\n"
                for reason in signal["reasons"]:
                    text += f"• {reason}\n"
                text += f"\n⏰ {time.strftime('%H:%M:%S')}"
                
                # Батчинг отправки
                sent_count = 0
                for i, user_id in enumerate(users):
                    if await send_message_safe(bot, user_id, text):
                        await log_signal(user_id, pair, side, signal["price"], signal["score"])
                        sent_count += 1
                    
                    if (i + 1) % BATCH_SEND_SIZE == 0:
                        await asyncio.sleep(1)
                    else:
                        await asyncio.sleep(BATCH_SEND_DELAY)
                
                LAST_SIGNALS[key] = now
                logger.info(f"Signal sent: {pair} {side} to {sent_count} users")
                
        except Exception as e:
            logger.error(f"Signal analyzer error: {e}")
        
        await asyncio.sleep(30)