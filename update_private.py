import asyncio
from datetime import datetime
import re
import urllib.parse
from playwright.async_api import async_playwright

WEB_URL = "https://p.kfwl.lol/https://happ.dska.su/https://sub.67vpn.monster/V4XtpRqVJ8umZbvX?h=6d0065eef10e3dfa"
OUTPUT_FILE = "privateWLunlocker.txt"


def rename_by_keywords(vless_url: str, index: int) -> str:
    if "#" in vless_url:
        base_url, raw_tag = vless_url.split("#", 1)
    else:
        base_url = vless_url
        raw_tag = ""

    decoded_name = urllib.parse.unquote(raw_tag)

    num_match = re.search(r"\d+", decoded_name)
    num = num_match.group(0) if num_match else str(index)

    if "Белые списки" in decoded_name or "БС" in decoded_name:
        new_name = f"🇷🇺Все страны - АВТО - БС #{num}"
    elif "Автовыбор" in decoded_name:
        new_name = f"⚡ Автовыбор #{num}"
    else:
        new_name = f"💣 @wlunlocker | №{index}"

    encoded_name = urllib.parse.quote(new_name)

    return f"{base_url}#{encoded_name}"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await page.goto(WEB_URL, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        content = await page.content()

        raw_keys = re.findall(r"vless://[^\s<\"']+", content)

        clean_keys = []
        for key in raw_keys:
            if (
                "HWID" not in key
                and "устройства" not in key
                and "0.0.0.0:1" not in key
            ):
                clean_keys.append(key)

        unique_keys = list(dict.fromkeys(clean_keys))

        await browser.close()

        if not unique_keys:
            exit(1)

        renamed_keys = [
            rename_by_keywords(key, i + 1)
            for i, key in enumerate(unique_keys)
        ]

        today = datetime.now().strftime("%d.%m.%y")

        header = [
            "# profile-title: 💣ПРИВАТНАЯ @wlunlocker",
            f"# last-update: {today}",
            f"# count: {len(renamed_keys)}",
            "",
        ]

        file_content = "\n".join(header) + "\n" + "\n".join(renamed_keys)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(file_content)


if __name__ == "__main__":
    asyncio.run(main())
