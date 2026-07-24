import asyncio
from datetime import datetime
import re
import time
import urllib.parse
from playwright.async_api import async_playwright

BASE_WEB_URL = "https://p.kfwl.lol/https://happ.dska.su/https://sub.67vpn.monster/V4XtpRqVJ8umZbvX?h=6d0065eef10e3dfa"
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
            r"[\U0001F1E6-\U0001F1FF]{2}\s*([A-Za-zА-Яа-я]+)", decoded_name
        )
        country = (
            country_match.group(1).capitalize()
            if country_match
            else "Все страны"
        )
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


async def main():
    # Динамический хвост времени ломает кэш прокси-сервера
    WEB_URL = f"{BASE_WEB_URL}&_t={int(time.time())}"
    
    print("🚀 Запуск парсера...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"🌐 Переходим по ссылке: {WEB_URL}")
        await page.goto(WEB_URL, wait_until="networkidle")
        
        print("⏳ Ждем 10 секунд прогрузки страницы...")
        await page.wait_for_timeout(10000)

        content = await page.content()
        print(f"📄 Размер полученного HTML: {len(content)} символов")

        raw_keys = re.findall(r"vless://[^\s<\"']+", content)
        print(f"🔍 Найдено сырых ссылок: {len(raw_keys)}")

        clean_keys = []
        for key in raw_keys:
            if (
                "HWID" not in key
                and "устройства" not in key
                and "0.0.0.0:1" not in key
            ):
                clean_keys.append(key)

        unique_keys = list(dict.fromkeys(clean_keys))
        print(f"✅ Уникальных чистых серверов после фильтра: {len(unique_keys)}")

        await browser.close()

        if not unique_keys:
            print("❌ Серверы не найдены! Выход.")
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
        
        print(f"💾 Файл успешно сохранен! Записано серверов: {len(renamed_keys)}")


if __name__ == "__main__":
    asyncio.run(main())
