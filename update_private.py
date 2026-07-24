import urllib.request
import base64
import re
import urllib.parse
from datetime import datetime

# ПРЯМАЯ ссылка на твою подписку, без всяких прокладок-визуализаторов happ.dska.su!
DIRECT_URL = "https://sub.67vpn.monster/V4XtpRqVJ8umZbvX?h=6d0065eef10e3dfa"
# Если прямая не сработает, раскомментируй строку ниже (через прокси):
# DIRECT_URL = "https://p.kfwl.lol/https://sub.67vpn.monster/V4XtpRqVJ8umZbvX?h=6d0065eef10e3dfa"

OUTPUT_FILE = "privateWLunlocker.txt"


def rename_by_keywords(vless_url: str, index: int) -> str:
    if "#" in vless_url:
        base_url, raw_tag = vless_url.split("#", 1)
    else:
        base_url = vless_url
        raw_tag = ""

    decoded_name = urllib.parse.unquote(raw_tag)
    lower_name = decoded_name.lower()

    is_auto = "авто" in lower_name

    if "белые" in lower_name or "бс" in lower_name:
        mode = "БС"
    else:
        mode = "ЧС"

    flags = re.findall(r"[\U0001F1E6-\U0001F1FF]{2}", decoded_name)

    if "🇪🇺" in decoded_name or "европа" in lower_name:
        flag = "🇪🇺"
        country = "Европа"
    elif flags and flags[0] != "🇷🇺":
        flag = flags[0]
        country_match = re.search(
            r"[\U0001F1E6-\U0001F1FF]{2}\s*([A-Za-zА-Яа-яЁё\s\-]+)", decoded_name
        )
        if country_match:
            country = country_match.group(1).strip().capitalize()
        else:
            country = "Все страны"
    else:
        flag = "🇷🇺"
        country = "Все страны"

    if country == "Все страны":
        is_auto = True

    if is_auto:
        flag_prefix = f"{flag}⚡ "
    else:
        flag_prefix = f"{flag} "

    parts = [f"{flag_prefix}{country}", mode]
    if is_auto:
        parts.append("АВТО")

    new_name = " - ".join(parts) + f" #{index}"
    encoded_name = urllib.parse.quote(new_name)
    return f"{base_url}#{encoded_name}"


def main():
    print(f"🌐 Скачиваем сырую подписку напрямую: {DIRECT_URL}")
    
    # Маскируемся под VPN-клиент, чтобы сервер отдал нам чистый Base64 код подписки
    req = urllib.request.Request(
        DIRECT_URL, 
        headers={'User-Agent': 'v2rayN/6.23 Sing-box/1.8.0'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8').strip()
            print("✅ Данные успешно скачаны!")
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")
        exit(1)
        
    print("🔓 Раскодируем подписку...")
    try:
        # Подписки VPN всегда зашифрованы в Base64, расшифровываем:
        decoded_content = base64.b64decode(content).decode('utf-8')
    except Exception:
        # На случай, если админ сервера убрал шифрование
        decoded_content = content
        
    raw_keys = re.findall(r"vless://[^\s<\"']+", decoded_content)
    print(f"🔍 Найдено сырых ссылок: {len(raw_keys)}")

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
    print(f"✅ Уникальных чистых серверов после фильтра: {len(unique_keys)}")

    if not unique_keys:
        print("❌ Ошибка: Не удалось найти ни одной чистой VLESS ссылки!")
        exit(1)

    renamed_keys = [rename_by_keywords(key, i + 1) for i, key in enumerate(unique_keys)]

    today = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    uploaded_bytes = 83732298752
    downloaded_bytes = 0
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

    print(f"✅ Успешно обновлено! Файл сохранен. Записано серверов: {len(renamed_keys)}")

if __name__ == "__main__":
    main()
