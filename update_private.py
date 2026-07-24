import asyncio
from datetime import datetime
import re
import time
import urllib.parse
import base64
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
    nocache_url = f"{BASE_WEB_URL}&_t={int(time.time())}"
    print(f"🌐 Запрос свежих данных: {nocache_url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            permissions=['clipboard-read', 'clipboard-write']
        )
        
        page = await context.new_page()

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

        await page.route("**/*", lambda route: route.continue_())
        await page.goto(nocache_url, wait_until="networkidle")
        
        print("⏳ Ждем 10 секунд для прогрузки скриптов сайта...")
        await page.wait_for_timeout(10000)

        print("🖱️ Ищем кнопку 'Скопировать все ключи'...")
        buttons = await page.locator("button, a, div[role='button']").all()
        
        clicked = False
        for btn in buttons:
            try:
                text = await btn.inner_text()
                if "скопировать все ключи" in text.lower():
                    print(f"🎯 Найдена целевая кнопка: '{text.strip()}' -> Кликаем!")
                    await btn.click(force=True, timeout=2000)
                    await page.wait_for_timeout(2000)
                    clicked = True
                    break  # Выходим из цикла, больше ничего не кликаем
            except:
                pass
        
        if not clicked:
            print("⚠️ Кнопка 'Скопировать все ключи' не найдена!")

        clipboard_text = await page.evaluate("window.capturedClipboard")

        if "vless://" not in clipboard_text:
            print("⚠️ В буфере пусто. Пробуем раскодировать страницу как Base64 подписку...")
            try:
                inner_text = await page.evaluate("document.body.innerText")
                decoded_b64 = base64.b64decode(inner_text.strip()).decode('utf-8')
                if "vless://" in decoded_b64:
                    print("✅ Найдены ключи в формате Base64!")
                    clipboard_text += "\n" + decoded_b64
            except:
                pass
                
            content = await page.content()
            clipboard_text += "\n" + urllib.parse.unquote(content)

        await browser.close()

        raw_keys = re.findall(r"vless://[^\s<\"']+", clipboard_text)
        print(f"🔍 Найдено сырых ссылок: {len(raw_keys)}")

        clean_keys = []
        for key in raw_keys:
            # Улучшенный фильтр с приведением к нижнему регистру для надежности
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
            print("👇 ВОТ ЧТО САЙТ ОТДАЛ ДО ФИЛЬТРАЦИИ (посмотри, на что он ругается):")
            for rk in raw_keys:
                print(" ->", urllib.parse.unquote(rk))
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

        print(f"✅ Успешно обновлено! Серверов записано: {len(renamed_keys)}")


if __name__ == "__main__":
    asyncio.run(main())
