from datetime import datetime
import re
import urllib.parse
import urllib.request
import base64

RAW_URL = "https://raw.githubusercontent.com/SoloRepozSF/Key-for-vpn/refs/heads/main/%D0%95%D1%81%D0%BB%D0%B8%20%D0%B1%20%D1%8F%20%D0%BF%D0%BE%D1%88%D0%B5%D0%BB%2010%20%D1%82%D0%BE%20%D1%82%D0%B2%D0%BE%D0%B9%20%D0%BF%D0%B0%D1%85%D0%B0%D0%BD%20%D0%BF%D0%BE%D1%88%D0%B5%D0%BB%20%D0%B1%D1%8B%20%D0%B2%205"
MY_KEYS_FILE = "my_keys.txt"
OUTPUT_FILE = "privateWLunlocker.txt"
MAX_SERVERS = 60

HEADER_WIFI_TITLE = "⬇️ Обычный VPN (Wi-Fi) ⬇️"
HEADER_LTE_TITLE = "⬇️ Обход глушилок (LTE) ⬇️"

DUMMY_UUID = "00000000-0000-0000-0000-000000000000"

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
    ("🇳🇴", "Норвегия", ["no", "nor", "norway", "норвегия", "🇳🇴"]),
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
    ("🇨🇳", "Китай", ["cn", "chn", "china", "китай", "🇨🇳"]),
]


def create_header_node(title: str) -> str:
    """Создает пустой нерабочий сервер для использования в качестве визуальной плашки"""
    encoded_title = urllib.parse.quote(title)
    return f"vless://{DUMMY_UUID}@127.0.0.1:1?type=tcp#{encoded_title}"


def detect_country_and_flag(text: str):
    lower_text = text.lower()

    for flag, country_name, keywords in COUNTRIES_DB:
        for kw in keywords:
            if len(kw) > 3 or not kw.isalnum():
                if kw in lower_text:
                    return flag, country_name
            else:
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, lower_text):
                    return flag, country_name

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

    return "🇷🇺", "Все страны"


def parse_key_info(vless_url: str):
    """Разбирает ключ и возвращает метаданные для формирования имени"""
    if "#" in vless_url:
        base_url, raw_tag = vless_url.split("#", 1)
    else:
        base_url = vless_url
        raw_tag = ""

    decoded_name = urllib.parse.unquote(raw_tag)
    lower_name = decoded_name.lower()

    is_bs = "белые" in lower_name or "бс" in lower_name

    if "быстрый" in lower_name or "антизаглушки" in lower_name:
        flag = "🇪🇺"
        country = "Европа"
        is_bs = False
        is_auto = True
    else:
        clean_base = decoded_name.split("#")[0].strip()
        base_parts = [p.strip() for p in clean_base.split("-")]
        search_target = base_parts[0] if base_parts else clean_base

        flag, country = detect_country_and_flag(search_target)
        is_auto = "авто" in lower_name or country == "Все страны"

    if is_bs:
        symbol = "⚡📱"
    elif country in "Европа":
        symbol = "⚡📺"
    elif country in "Франция":
        symbol = "⚡🤖"
    elif country == "Германия":
        symbol = "⚡🤖"
    elif country == "Нидерланды":
        symbol = "⚡"
    elif country == "Великобритания", "Румыния", "Канада", "Эстония":
        symbol = "⚡"
    elif country == "США":
        symbol = "📺"
    elif country in "Польша":
        symbol = "🎮"
    elif country in ["Норвегия", "Все страны"]:
        symbol = "🏴‍☠️"
    else:
        symbol = "❓"

    return {
        "base_url": base_url,
        "is_bs": is_bs,
        "flag": flag,
        "symbol": symbol,
        "country": country,
        "is_auto": is_auto,
    }


def build_vless_url(info: dict, index: int) -> str:
    parts = [f"{info['flag']}{info['symbol']} {info['country']}"]
    if info["is_auto"]:
        parts.append("АВТО")

    new_name = " - ".join(parts) + f" #{index}"
    encoded_name = urllib.parse.quote(new_name)
    return f"{info['base_url']}#{encoded_name}"


def clean_keys_list(raw_keys):
    clean_keys = []
    for key in raw_keys:
        key_lower = urllib.parse.unquote(key).lower()
        if (
            "hwid" not in key_lower
            and "устройств" not in key_lower
            and "0.0.0.0:1" not in key_lower
            and DUMMY_UUID not in key_lower
        ):
            clean_keys.append(key)
    return list(dict.fromkeys(clean_keys))


def main():
    my_raw_keys = []
    try:
        with open(MY_KEYS_FILE, "r", encoding="utf-8") as f:
            my_raw_keys = re.findall(r"vless://[^\s<\"']+", f.read())
    except FileNotFoundError:
        with open(MY_KEYS_FILE, "w", encoding="utf-8") as f:
            f.write("# Вставляй сюда свои VLESS ссылки\n")

    print("🌐 Скачиваем автособранные данные...")
    req = urllib.request.Request(RAW_URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_text = response.read().decode("utf-8")
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")
        exit(1)

    lines = raw_text.splitlines()
    target_lines = lines[6:22]
    content_block = "\n".join(target_lines)
    auto_raw_keys = re.findall(r"vless://[^\s<\"']+", content_block)

    my_clean_keys = clean_keys_list(my_raw_keys)
    auto_clean_keys = clean_keys_list(auto_raw_keys)

    my_keys_to_use = my_clean_keys[:MAX_SERVERS]
    remaining_slots = MAX_SERVERS - len(my_keys_to_use)
    auto_keys_to_use = auto_clean_keys[:remaining_slots]

    all_keys = my_keys_to_use + auto_keys_to_use

    wifi_keys_info = []
    lte_keys_info = []

    for key in all_keys:
        info = parse_key_info(key)
        if info["is_bs"]:
            lte_keys_info.append(info)
        else:
            wifi_keys_info.append(info)

    final_servers = []
    current_index = 1

    if wifi_keys_info:
        final_servers.append(create_header_node(HEADER_WIFI_TITLE))
        for info in wifi_keys_info:
            final_servers.append(build_vless_url(info, current_index))
            current_index += 1

    if lte_keys_info:
        final_servers.append(create_header_node(HEADER_LTE_TITLE))
        for info in lte_keys_info:
            final_servers.append(build_vless_url(info, current_index))
            current_index += 1

    total_count = len(wifi_keys_info) + len(lte_keys_info)

    today = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    used_traffic_bytes = 91363817226240
    uploaded_bytes = 0
    downloaded_bytes = used_traffic_bytes
    total_bytes = 0
    expire_timestamp = 1784920013

    header = [
        "# profile-title: 💎ПРИВАТНАЯ (VPN + БС)",
        f"# subscription-userinfo: upload={uploaded_bytes}; download={downloaded_bytes}; total={total_bytes}; expire={expire_timestamp}",
        "# profile-update-interval: 1",
        "# announce: ⚡ - Высокая скорость, 🤖 - Нейросети, 📺 - Быстрый Youtube, 🏴‍☠️ - Торренты, 🎮 - Игры, 📱 - Обход LTE, ❓ - Статус неизвестен",
        "# profile-web-page-url: https://github.com/wlunlocker/anti-rkn",
        "# support-url: https://t.me/wlunlocker",
        f"# last-update: {today}",
        f"# count: {total_count}",
        "",
    ]

    lines_out = header + final_servers
    raw_content = "\n".join(lines_out) + "\n"

    encoded_content = base64.b64encode(raw_content.encode("utf-8")).decode("utf-8")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(encoded_content)

    print(
        f"🚀 Готово! Серверов Wi-Fi: {len(wifi_keys_info)}, LTE (БС): {len(lte_keys_info)}. Всего: {total_count}."
    )
    print(f"🔒 Файл {OUTPUT_FILE} успешно зашифрован в Base64!")


if __name__ == "__main__":
    main()
