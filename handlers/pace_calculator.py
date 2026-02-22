# -*- coding: utf-8 -*-
"""
Калькулятор темпа для бега: темп, дистанция, время, скорость.
Пользователь вводит любые два известных значения — бот считает остальные.
"""

import re
from typing import Optional, Tuple

from telegram import Update
from telegram.ext import ContextTypes

# Связи: скорость (км/ч) = 60 / темп (мин/км), время (мин) = дистанция (км) * темп, дистанция = время / темп


def _parse_pace(s: str) -> Optional[float]:
    """Парсит темп: 5:30, 5.5, 6:00 -> минуты на км."""
    s = s.strip().replace(",", ".")
    # 5:30 или 6:00
    m = re.match(r"^(\d+):(\d{2})$", s)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 60.0
    # 5.5 или 6
    m = re.search(r"(\d+\.?\d*)\s*(?:мин/км|min/km|/км|/km)?", s, re.I)
    if m:
        return float(m.group(1))
    return None


def _parse_distance(s: str) -> Optional[float]:
    """Парсит дистанцию в км: 10 км, 21.1, полумарафон, марафон."""
    s_lower = s.strip().lower()
    if "полумарафон" in s_lower or "half" in s_lower:
        return 21.0975
    if "марафон" in s_lower and "полу" not in s_lower or "marathon" in s_lower:
        return 42.195
    m = re.search(r"(\d+\.?\d*)\s*(?:км|km|k)(?!\s*/\s*ч)", s_lower, re.I)
    if m:
        return float(m.group(1))
    m = re.search(r"^(\d+\.?\d*)\s*$", s.strip())
    if m:
        return float(m.group(1))
    return None


def _parse_time(s: str) -> Optional[float]:
    """Парсит время в минутах: 55, 1:30, 1:30:00, 1ч 30мин."""
    s = s.strip().lower().replace(" ", "")
    # 1:30:00
    m = re.match(r"^(\d+):(\d{2}):(\d{2})$", s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2)) + int(m.group(3)) / 60.0
    # 1:30 или 55:00
    m = re.match(r"^(\d+):(\d{2})$", s)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if a > 24:
            return a + b / 60.0
        return a * 60 + b
    # 90 мин, 90мин
    m = re.search(r"(\d+)\s*мин", s)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+)\s*ч", s)
    if m:
        return float(m.group(1)) * 60
    m = re.search(r"^(\d+\.?\d*)$", s)
    if m:
        return float(m.group(1))
    return None


def _parse_speed(s: str) -> Optional[float]:
    """Парсит скорость км/ч: 10 км/ч, 12.5."""
    m = re.search(r"(\d+\.?\d*)\s*км\s*/\s*ч", s, re.I)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+\.?\d*)\s*km/h", s, re.I)
    if m:
        return float(m.group(1))
    return None


def parse_input(text: str) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    Парсит строку пользователя. Возвращает (pace, distance_km, time_min, speed_kmh).
    """
    text_lower = text.lower().strip()
    pace = None
    distance = None
    time_min = None
    speed = None

    # Специальные дистанции
    if "полумарафон" in text_lower or "half" in text_lower:
        distance = 21.0975
    elif "марафон" in text_lower and "полу" not in text_lower:
        distance = 42.195

    # Скорость: 12 км/ч
    m = re.search(r"(\d+\.?\d*)\s*км\s*/\s*ч", text, re.I)
    if m:
        speed = float(m.group(1))

    # Темп 5:30 (мин/км)
    for m in re.finditer(r"\b(\d+):(\d{2})\b", text):
        a, b = int(m.group(1)), int(m.group(2))
        if 2 <= a <= 20 and 0 <= b < 60 and pace is None:
            pace = a + b / 60.0
            break

    # Дистанция: 10 км, 10км, 21.1
    m = re.search(r"(\d+\.?\d*)\s*(?:км|km|k)\b", text_lower)
    if m and distance is None:
        distance = float(m.group(1))
    # 5 км 500 м (сначала комбо, потом отдельные метры)
    m = re.search(r"(\d+)\s*(?:км|km)\s*(\d+)\s*(?:м|m)\b", text_lower)
    if m and distance is None:
        distance = float(m.group(1)) + float(m.group(2)) / 1000.0
    # Метры: 500 м, 1000 м
    m = re.search(r"(\d+\.?\d*)\s*(?:м|m|метров?)\b", text_lower)
    if m and distance is None:
        distance = float(m.group(1)) / 1000.0

    # Время: 1:30:45 (ч:мин:сек)
    m = re.search(r"(\d+):(\d{2}):(\d{2})", text)
    if m and time_min is None:
        time_min = int(m.group(1)) * 60 + int(m.group(2)) + int(m.group(3)) / 60.0
    # Время: 55:30 (мин:сек) или 1:30 (ч:мин). Не считаем X:YY временем, если это типичный темп (2–20 мин)
    m = re.search(r"(\d+):(\d{2})(?::(\d{2}))?", text)
    if m and time_min is None:
        a, b = int(m.group(1)), int(m.group(2))
        c = int(m.group(3)) if m.group(3) else 0
        if m.group(3) is not None:
            time_min = a * 60 + b + c / 60.0
        elif 2 <= a <= 20 and 0 <= b < 60:
            pass
        elif a > 23 or (a > 12 and b < 60):
            time_min = a + b / 60.0
        else:
            time_min = a * 60 + b
    # 1ч 30мин 45сек, 55 мин 30 сек
    m = re.search(r"(\d+)\s*ч\s*(\d+)?\s*мин\s*(\d+)?\s*сек?", text_lower)
    if m and time_min is None:
        time_min = float(m.group(1)) * 60 + float(m.group(2) or 0) + float(m.group(3) or 0) / 60.0
    m = re.search(r"(\d+)\s*мин\s*(\d+)?\s*сек?", text_lower)
    if m and time_min is None:
        time_min = float(m.group(1)) + float(m.group(2) or 0) / 60.0
    m = re.search(r"(\d+)\s*ч\s*(\d+)?", text_lower)
    if m and time_min is None:
        time_min = float(m.group(1)) * 60 + (float(m.group(2) or 0))
    m = re.search(r"(\d+)\s*мин", text_lower)
    if m and time_min is None:
        time_min = float(m.group(1))
    m = re.search(r"(\d+)\s*сек", text_lower)
    if m and time_min is None and not re.search(r"\d+\s*мин", text_lower):
        time_min = float(m.group(1)) / 60.0

    # Два числа подряд: 10 55 -> дистанция и время или темп и дистанция
    numbers = [float(x) for x in re.findall(r"\d+\.?\d*", text)]
    if distance is None and time_min is None and len(numbers) >= 2:
        a, b = numbers[0], numbers[1]
        if 0.5 <= a <= 50 and 5 <= b <= 400:
            distance = a
            time_min = b
    if pace is not None and distance is None and len(numbers) >= 1:
        for n in numbers:
            if 0.5 <= n <= 50 and (n >= 10 or abs(n - pace) > 0.5):
                distance = n
                break
    if pace is None and distance is None and len(numbers) >= 2:
        a, b = numbers[0], numbers[1]
        if 3 <= a <= 15 and 0.5 <= b <= 50:
            pace = a
            distance = b
    if distance is None and len(numbers) == 1 and 0.5 <= numbers[0] <= 50:
        distance = numbers[0]
    return (pace, distance, time_min, speed)


def compute(
    pace: Optional[float],
    distance: Optional[float],
    time_min: Optional[float],
    speed: Optional[float],
) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    По двум известным величинам вычисляет остальные.
    pace мин/км, distance км, time_min мин, speed км/ч.
    """
    if sum(x is not None for x in (pace, distance, time_min, speed)) < 2:
        return (pace, distance, time_min, speed)
    # speed = 60/pace, pace = 60/speed, time = distance*pace, distance = time/pace
    while True:
        if pace is not None and speed is None:
            speed = 60.0 / pace
            continue
        if speed is not None and pace is None:
            pace = 60.0 / speed
            continue
        if distance is not None and pace is not None and time_min is None:
            time_min = distance * pace
            continue
        if time_min is not None and pace is not None and distance is None:
            distance = time_min / pace
            continue
        if distance is not None and time_min is not None and pace is None:
            pace = time_min / distance
            continue
        if distance is not None and time_min is not None and speed is None:
            speed = distance / (time_min / 60.0)
            continue
        if speed is not None and time_min is not None and distance is None:
            distance = speed * (time_min / 60.0)
            continue
        if speed is not None and distance is not None and time_min is None:
            time_min = distance / speed * 60.0
            continue
        break
    return (pace, distance, time_min, speed)


def format_pace(pace_min: float) -> str:
    m = int(pace_min)
    s = round((pace_min - m) * 60)
    if s >= 60:
        s = 0
        m += 1
    return f"{m}:{s:02d}"


def format_time(minutes: float) -> str:
    total_sec = round(minutes * 60)
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    s = total_sec % 60
    parts = []
    if h > 0:
        parts.append(f"{h} ч")
    if m > 0 or (h == 0 and s == 0):
        parts.append(f"{m} мин")
    if s > 0 or (h == 0 and m == 0):
        parts.append(f"{s} сек")
    return " ".join(parts)


def format_distance(km: float) -> str:
    if km < 0.001:
        return f"{km * 1000:.0f} м"
    if km >= 1 and km == round(km, 3):
        return f"{km:.0f} км"
    if km < 1 or (km * 1000) == round(km * 1000):
        return f"{km:.2f} км ({int(round(km * 1000))} м)"
    return f"{km:.2f} км"


def format_result(pace: Optional[float], distance: Optional[float], time_min: Optional[float], speed: Optional[float]) -> str:
    lines = ["🧮 <b>Калькулятор темпа</b>\n"]
    if pace is not None:
        lines.append(f"⏱ Темп: <b>{format_pace(pace)}</b> /км")
    if distance is not None:
        lines.append(f"📏 Дистанция: <b>{format_distance(distance)}</b>")
    if time_min is not None:
        lines.append(f"🕐 Время: <b>{format_time(time_min)}</b>")
    if speed is not None:
        lines.append(f"🚀 Скорость: <b>{speed:.2f}</b> км/ч")
    return "\n".join(lines)


PACER_HELP = """🧮 <b>Калькулятор темпа</b>

Введите <b>два</b> известных значения в одном сообщении, например:
• <b>10 км 55 мин 30 сек</b> — дистанция и время
• <b>5:30 10 км</b> — темп и дистанция
• <b>1000 м 4 мин</b> — метры и время
• <b>5 км 500 м 28 мин</b> — дистанция с метрами и время
• <b>55:30 10</b> — время мин:сек и дистанция
• <b>1:30:45 полумарафон</b> — время ч:мин:сек и дистанция
• <b>12 км/ч 30 мин</b> — скорость и время

Единицы: <b>км</b>, <b>м</b> (метры), <b>мин</b>, <b>сек</b>, <b>ч</b>, мин/км, км/ч. Темп: 5:30 или 5.5."""


async def show_pace_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать подсказку калькулятора и ждать ввод."""
    context.user_data["expect"] = "pace"
    await update.message.reply_text(PACER_HELP, parse_mode="HTML")


def handle_pace_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """
    Обработать сообщение как ввод для калькулятора. Возвращает текст ответа или None.
    """
    text = (update.message.text or "").strip()
    if not text:
        return None
    pace, distance, time_min, speed = parse_input(text)
    given = sum(1 for x in (pace, distance, time_min, speed) if x is not None)
    if given < 2:
        return "Введите хотя бы два значения, например: 10 км 55 мин"
    pace, distance, time_min, speed = compute(pace, distance, time_min, speed)
    return format_result(pace, distance, time_min, speed)
