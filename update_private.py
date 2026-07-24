import asyncio
from datetime import datetime
import re
import time
import urllib.parse
import base64
from playwright.async_api import async_playwright

# Твоя полная ссылка на сайт с кнопкой
WEB_URL = "https://p.kfwl.lol/https://happ.dska.su/https://sub.67vpn.monster/V4XtpRqVJ8umZbvX?h=6d0065eef10e3dfa"
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


async def main():
    print(f"🌐 Открываем сайт: {WEB_URL}")

    async with async_playwright() as p:
        # Запускаем браузер с параметрами, чтобы сайт думал, что это реальный человек за ПК
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            permissions=['clipboard-read', 'clipboard-write']
        )
        
        page = await context.new_page()

        # Перехватываем буфер обмена
        await page.add_init_script("""
            window.capturedClipboard = "";
            
            Object.defineProperty(navigator, 'clipboard', {
                value: {
                    writeText: async function(text) {
                        window.capturedClipboard += "\\n" + text;
                        return Promise.resolve();
                    },
                    readText: async function() {
                        return window.capturedClipboard;
                    }
                },
                writable: true,
                configurable: true
            });

            const originalExecCommand = document.execCommand;
            document.execCommand = function(commandId, showUI, value) {
                if (commandId.toLowerCase() === 'copy') {
                    const selectedText = window.getSelection().toString();
                    if (selectedText) {
                        window.capturedClipboard += "\\n" + selectedText;
                    } else {
                        const activeElement = document.activeElement;
                        if (activeElement && (activeElement.tagName === 'TEXTAREA' || activeElement.tagName === 'INPUT')) {
                            window.capturedClipboard += "\\n" + activeElement.value;
                        }
                    }
                }
                return originalExecCommand.apply(document, arguments);
            };
        """)

        # Переходим на страницу сайта со случайным параметром времени, чтобы не было кэша
        target_url = f"{WEB_URL}&_nocache={int(time.time())}"
        await page.goto(target_url, wait_until="networkidle")
        
        print("⏳ Ждем 6 секунд для прогрузки интерфейса сайта...")
        await page.wait_for_timeout(6000)

        print("🖱️ Ищем кнопку 'Скопировать все ключи'...")
        
        # Ищем кнопку по точному или частичному совпадению текста
        clicked = False
        buttons = await page.locator("button, a, div, span").all()
        
        for btn in buttons:
            try:
                text = await btn.inner_text()
                # Ищем именно кнопку копирования всех ключей
                if "скопировать все ключи" in text.lower() or "скопировать все" in text.lower():
                    print(f"🎯 Найдена кнопка: '{text.strip()}' -> Кликаем!")
                    await btn.click(force=True)
                    await page.wait_for_timeout(2500) # Ждем пока скопируется
                    clicked = True
                    break
            except:
                pass
        
        if not clicked:
            print("⚠️ Кнопка не найдена через текст, пробуем кликнуть по любому элементу с иконкой копирования...")
            # Запасной вариант: клик по первой попавшейся кнопке на странице
            try:
                await page.locator("button").first.click(force=True)
                await page.wait_for_timeout(2000)
            except:
                pass

        # Забираем то, что попало в буфер или на страницу
        clipboard_text = await page.evaluate("window.capturedClipboard")
        
        # Если в буфере пусто, забираем весь текст со страницы (на случай если ключи просто выведены текстом)
        if "vless://" not in clipboard_text:
            print("⚠️ В буфере пусто, собираем весь текст со страницы...")
            page_text = await page.evaluate("document.body.innerText")
            clipboard_text += "\n" + page_text

        await browser.close()

        # Ищем vless ссылки
        raw_keys = re.findall(r"vless://[^\s<\"']+", clipboard_text)
        print(f"🔍 Найдено сырых ссылок: {len(raw_keys)}")

        clean_keys = []
        for key in raw_keys:
            key_lower = urllib.parse.unquote(key).lower()
            # Фильтруем ошибки лимитов и пустые заглушки
            if (
                "hwid" not in key_lower
                and "устройств" not in key_lower
                and "лимит" not in key_lower
                and "0.0.0.0:1" not in key_lower
            ):
                clean_keys.append(key)

        unique_keys = list(dict.fromkeys(clean_keys))
        print(f"✅ Уникальных чистых серверов после фильтра: {len(unique_keys)}")

        if not unique_keys:
            print("❌ Ошибка: Сайт всё еще отдает лимит или пустые ключи!")
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

        print(f"💾 Успешно! Записано серверов: {len(renamed_keys)}")


if __name__ == "__main__":
    asyncio.run(main())
