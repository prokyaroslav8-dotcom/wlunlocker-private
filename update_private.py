from datetime import datetime
import re
import urllib.parse

OUTPUT_FILE = "privateWLunlocker.txt"

# База стран: флаг, правильное название на русском, список ключевых слов/кодов
COUNTRIES_DB = [
    ("🇪🇺", "Европа", ["eu", "eur", "europe", "европа", "🇪🇺"]),
    ("🇺🇸", "США", ["us", "usa", "сша", "united states", "америка", "america", "🇺🇸"]),
    ("🇩🇪", "Германия", ["de", "ger", "deu", "germany", "германия", "🇩🇪"]),
    ("🇳🇱", "Нидерланды", ["nl", "nld", "netherlands", "нидерланды", "голландия", "holland", "🇳🇱"]),
    ("🇫🇷", "Франция", ["fr", "fra", "france", "франция", "🇫🇷"]),
    ("🇬🇧", "Великобритания", ["gb", "gbr", "uk", "united kingdom", "england", "великобритания", "англия", "юкей", "🇬🇧"]),
    ("🇹🇷", "Турция", ["tr", "tur", "turkey", "турция", "🇹🇷"]),
    ("🇫🇮", "Финляндия", ["fi", "fin", "finland", "финляндия", "🇫🇮"]),
    ("🇵🇱", "Польша", ["pl", "pol", "poland", "польша", "🇵🇱"]),
    ("🇸🇪", "Швеция", ["se", "swe", "sweden", "швеция", "🇸🇪"]),
    ("🇰🇿", "Казахстан", ["kz", "kaz", "kazakhstan", "казахстан", "🇰🇿"]),
    ("🇦🇪", "ОАЭ", ["ae", "uae", "оаэ", "эмираты", "dubai", "дубай", "🇦🇪"]),
    ("🇯🇵", "Япония", ["jp", "jpn", "japan", "япония", "🇯🇵"]),
    ("🇰🇷", "Корея", ["kr", "kor", "korea", "корея", "🇰🇷"]),
    ("🇸🇬", "Сингапур", ["sg", "sgp", "singapore", "сингапур", "🇸🇬"]),
    ("🇭🇰", "Гонконг", ["hk", "hkg", "hong kong", "гонконг", "🇭🇰"]),
    ("🇨🇦", "Канада", ["ca", "can", "canada", "канада", "🇨🇦"]),
    ("🇮🇹", "Италия", ["it", "ita", "italy", "италия", "🇮🇹"]),
    ("🇪🇸", "Испания", ["es", "esp", "spain", "испания", "🇪🇸"]),
    ("🇨🇭", "Швейцария", ["ch", "che", "switzerland", "швейцария", "🇨🇭"]),
    ("🇦🇹", "Австрия", ["at", "aut", "austria", "австрия", "🇦🇹"]),
    ("🇨🇿", "Чехия", ["cz", "cze", "czechia", "czech", "чехия", "🇨🇿"]),
    ("🇷🇴", "Румыния", ["ro", "rou", "romania", "румыния", "🇷🇴"]),
    ("🇧🇬", "Болгария", ["bg", "bgr", "bulgaria", "болгария", "🇧🇬"]),
    ("🇷🇸", "Сербия", ["rs", "srb", "serbia", "сербия", "🇷🇸"]),
    ("🇦🇲", "Армения", ["am", "arm", "armenia", "армения", "🇦🇲"]),
    ("🇬🇪", "Грузия", ["ge", "geo", "georgia", "грузия", "🇬🇪"]),
    ("🇲🇩", "Молдова", ["md", "mda", "moldova", "молдова", "молдавия", "🇲🇩"]),
    ("🇪🇪", "Эстония", ["ee", "est", "estonia", "эстония", "🇪🇪"]),
    ("🇱🇻", "Латвия", ["lv", "lva", "latvia", "латвия", "🇱🇻"]),
    ("🇱🇹", "Литва", ["lt", "ltu", "lithuania", "литва", "🇱🇹"]),
    ("🇮🇳", "Индия", ["in", "ind", "india", "индия", "🇮🇳"]),
    ("🇧🇷", "Бразилия", ["br", "bra", "brazil", "бразилия", "🇧🇷"]),
    ("🇦🇺", "Австралия", ["au", "aus", "australia", "австралия", "🇦🇺"]),
]


def detect_country_and_flag(text: str):
    lower_text = text.lower()

    # 1. Сначала ищем совпадения по нашей расширенной базе
    for flag, country_name, keywords in COUNTRIES_DB:
        for kw in keywords:
            # Если ключевое слово длинное или это смайлик — ищем как подстроку
            if len(kw) > 3 or not kw.isalnum():
                if kw in lower_text:
                    return flag, country_name
            # Если это 2-3 буквенный код — ищем как отдельное слово (чтобы не путать с обычным текстом)
            else:
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, lower_text):
                    return flag, country_name

    # 2. Если в тексте есть какой-то другой смайлик флага (которого нет в базе)
    flags = re.findall(r"[\U0001F1E6-\U0001F1FF]{2}", text)
    if flags and flags[0] != "🇷🇺":
        flag = flags[0]
        country_match = re.search(
            r"[\U0001F1E6-\U0001F1FF]{2}\s*([A-Za-zА-Яа-яЁё\s\-]+)", text
        )
        if country_match:
            raw_country = country_match.group(1).strip()
            if raw_country.lower() in ["сша", "оаэ", "юк", "германия"]:
                country = raw_country.upper()
            else:
                country = raw_country.capitalize()
            return flag, country

    # 3. По умолчанию — Все страны
    return "🇷🇺", "Все страны"


def rename_by_keywords(vless_url: str, index: int) -> str:
    if "#" in vless_url:
        base_url, raw_tag = vless_url.split("#", 1)
    else:
        base_url = vless_url
        raw_tag = ""

    decoded_name = urllib.parse.unquote(raw_tag)
    lower_name = decoded_name.lower()

    # Определяем режим (БС / ЧС)
    if "белые" in lower_name or "бс" in lower_name:
        mode = "БС"
    else:
        mode = "ЧС"

    # Определяем АВТО
    is_auto = "авто" in lower_name

    # Очищаем от старых генераций (- ЧС, - БС, - АВТО, #1 и т.д.)
    clean_base = decoded_name.split("#")[0].strip()
    base_parts = [p.strip() for p in clean_base.split("-")]
    search_target = base_parts[0] if base_parts else clean_base

    # Распознаем страну и флаг
    flag, country = detect_country_and_flag(search_target)

    if country == "Все страны":
        is_auto = True

    if is_auto:
        flag_prefix = f"{flag}⚡ "
    else:
        flag_prefix = f"{flag} "

    # Формируем название строго по шаблону
    parts = [f"{flag_prefix}{country}", mode]
    if is_auto:
        parts.append("АВТО")

    new_name = " - ".join(parts) + f" #{index}"
    encoded_name = urllib.parse.quote(new_name)
    return f"{base_url}#{encoded_name}"


def main():
    print("📂 Читаем файл с сырыми ссылками...")
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Файл {OUTPUT_FILE} не найден!")
        exit(1)

    raw_keys = re.findall(r"vless://[^\s<\"']+", content)
    print(f"🔍 Найдено ссылок в файле: {len(raw_keys)}")

    clean_keys = []
    for key in raw_keys:
        key_lower = urllib.parse.unquote(key).lower()
        if (
            "hwid" not in key_lower
            and "устройств" not in key_lower
            and "0.0.0.0:1" not in key_lower
        ):
            clean_keys.append(key)

    unique_keys = list(dict.fromkeys(clean_keys))
    print(f"✅ Уникальных серверов после фильтра: {len(unique_keys)}")

    if not unique_keys:
        print("❌ Ошибка: В файле не найдено валидных VLESS ссылок!")
        exit(1)

    renamed_keys = [
        rename_by_keywords(key, i + 1)
        for i, key in enumerate(unique_keys)
    ]

    today = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    
    # 2.14 ТБ трафика
    used_traffic_bytes = 2352954883440 
    uploaded_bytes = 0
    downloaded_bytes = used_traffic_bytes
    total_bytes = 0
    expire_timestamp = 1807045200

    header = [
        "# profile-title: 💎ПРИВАТНАЯ (VPN + БС)",
        f"# subscription-userinfo: upload={uploaded_bytes}; download={downloaded_bytes}; total={total_bytes}; expire={expire_timestamp}",
        "# profile-update-interval: 1",
        "# announce: Приватные, 100% рабочие ключи. Больше подписок и прокси у нас в Telegram-канале или на сайте. Поддержка: @iduchamp",
        "# profile-web-page-url: https://github.com/wlunlocker/anti-rkn",
        "# support-url: https://t.me/wlunlocker",
        f"# last-update: {today}",
        f"# count: {len(renamed_keys)}",
        "",
    ]

    file_content = "\n".join(header) + "\n" + "\n".join(renamed_keys)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(file_content)

    print(f"💾 Успешно обработано! Записано красивых серверов: {len(renamed_keys)}")


if __name__ == "__main__":
    main()