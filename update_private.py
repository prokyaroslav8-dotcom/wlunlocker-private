from datetime import datetime
import re
import urllib.parse

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
    print("📂 Читаем файл с сырыми ссылками...")
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Файл {OUTPUT_FILE} не найден!")
        exit(1)

    raw_keys = re.findall(r"vless://[^\s<\"']+", content)
    print(f"🔍 Найдено сырых ссылок в файле: {len(raw_keys)}")

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
        print("❌ Ошибка: В файле не найдено валидных VLESS ссылок!")
        exit(1)

    renamed_keys = [
        rename_by_keywords(key, i + 1)
        for i, key in enumerate(unique_keys)
    ]

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

    print(f"💾 Успешно обработано! Записано красивых серверов: {len(renamed_keys)}")


if __name__ == "__main__":
    main()
