import re
from datetime import datetime, timedelta


PATTERN = re.compile(
    r'с\s+(\d{1,2})\s+([а-яё]+)\s+(\d{4})\s+по\s+(\d{1,2})\s+([а-яё]+)\s+(\d{4})',
    re.IGNORECASE
)

VIEWS_RE = re.compile(r'(больше|меньше)\s+([\d\s_]+)', re.IGNORECASE)
DATE_RE = re.compile(r'(\d{1,2})\s+([а-яё]+)\s+(\d{4})', re.IGNORECASE)
RELATIVE_RE = re.compile(r'\b(сегодня|вчера|неделю|месяц)\b', re.IGNORECASE)

MONTHS = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12'
}

def parse_number(text: str):

    match = VIEWS_RE.search(text)
    if not match:
        return None

    operator_word, raw_number = match.groups()
    operator = '>' if operator_word.lower() == 'больше' else '<'
    value = int(raw_number.replace(' ', ''))

    return [operator, value]

def find_dates(text, today=None):

    text = text.lower()

    match = PATTERN.search(text)
    if match:

        d1, m1, y1, d2, m2, y2 = match.groups()

        start_date = f"{y1}-{MONTHS[m1.lower()]}-{int(d1):02d}T00:00:00.000001+00:00"
        end_date = f"{y2}-{MONTHS[m2.lower()]}-{int(d2):02d}T23:59:59.999999+00:00"


        return [start_date, end_date]

    match = DATE_RE.search(text)
    if match:

        day, month_name, year = match.groups()
        month = MONTHS.get(month_name.lower())

        return [f"{year}-{month}-{int(day):02d}T23:59:59.999999+00:00"]

    if today is None:
        today = datetime.today()

    match_rel = RELATIVE_RE.search(text)

    if match_rel:

        word = match_rel.group(1).lower()

        if word == 'сегодня':
            return [today.isoformat()+'+00:00']
        elif word == 'вчера':
            dt = today - timedelta(days=1)
            return [dt.isoformat()+'+00:00']
        elif word == 'неделю':
            start = today - timedelta(days=7)
            end = today
            return [start.isoformat()+'+00:00', end.isoformat()+'+00:00']
        elif word == 'месяц':
            start = today - timedelta(days=30)
            end = today
            return [start.isoformat()+'+00:00', end.isoformat()+'+00:00']

    return None

def parse(text):
    if not text or not text.strip():
        return {"ok": False, "reason": "Пустое сообщение"}
    t = text.lower()

    # T1: сколько всего видео
    if re.search(r'\b(сколько\s+всего\s+видео|всего\s+видео\s+есть)\b', t):
        return {"ok": True, "template_id": "T1", "params": []}

    # T2: количество видео у креатора в период
    m = re.search(r'(?:креатор|автор|creator|creator_id|id)[\s:]*([0-9a-fA-F]{32})', t)
    if m:
        creator_id = m.group(1)
        dates = find_dates(t)

        if dates:

            return {"ok": True, "template_id": "T2", "params": [creator_id, dates[0][:19]+'+00:00', dates[1][:19]+'+00:00']}
        # если нет дат — считать за всё время
        start = datetime(2004,1,1,0,0,0)
        end = datetime.now().replace(hour=23, minute=59, second=59)
        return {"ok": True, "template_id": "T2", "params": [creator_id, start, end]}

    # T4: сумма приращений просмотров за дату/период (в тексте должны быть 'на сколько' + 'в сумме' + 'просмотр')
    if 'на сколько' in t and 'в сумме' in t and 'просмотр' in t:
        dates = find_dates(t)

        if len(dates) == 1:
            return {"ok": True, "template_id": "T4", "params": [dates[0][:10]]}
        if len(dates) == 2:
            return {"ok": True, "template_id": "T4_period", "params": [dates[0], dates[1]]}
        return {"ok": False, "reason": "Не указана дата или период"}

    # T5: сколько разных видео получали новые просмотры
    if re.search(r'сколько\s+(разных\s+)?видео.*(получал|получали|получить).*нов', t) and 'просмотр' in t:
        dates = find_dates(t)
        if len(dates) == 1:
            return {"ok": True, "template_id": "T5", "params": [dates[0][:10]]}
        if len(dates) == 2:
            return {"ok": True, "template_id": "T5_period", "params": [dates[0], dates[1]]}
        return {"ok": False, "reason": "Не указана дата или период"}

    # T3: видео с просмотрами
    # ищем упоминание просмотров и число
    if 'просмотр' in t:
        mnum = parse_number(t)

        if mnum:
            if mnum[0] == '>':
                print({"ok": True, "template_id": "T3_more", "params": [mnum[1]]})
                return {"ok": True, "template_id": "T3_more", "params": [mnum[1]]}
            if mnum[0] == '<':
                return {"ok": True, "template_id": "T3_less", "params": [mnum[1]]}
        return {"ok": False, "reason": "Нет упоминания числа просмотров"}

    return {"ok": False, "reason": "Бот не распознал фразу"}

if __name__ == "__main__":
    tests = [
        "Сколько всего видео есть в системе?",
        "Сколько видео у креатора с id 987 вышло с 1 ноября 2025 по 5 ноября 2025 включительно?",
        "Сколько видео набрало больше 100 000 просмотров за всё время?",
        "На сколько просмотров в сумме выросли все видео 28 ноября 2025?",
        "Сколько разных видео получали новые просмотры 27 ноября 2025?",
        "На сколько просмотров в сумме выросли все видео за вчера?",
    ]
    for s in tests:
        print("-" * 20)
        print("Фраза:", s)
        print("Результат:", parse(s))
