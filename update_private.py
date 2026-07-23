import asyncio
from datetime import datetime
import re
from playwright.async_api import async_playwright

WEB_URL = "https://p.kfwl.lol/https://happ.dska.su/https://sub.67vpn.monster/V4XtpRqVJ8umZbvX?h=6d0065eef10e3dfa"
OUTPUT_FILE = "privateWLunlocker.txt"


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

        today = datetime.now().strftime("%d.%m.%y")

        header = [
            "# profile-title: 💣ПРИВАТНАЯ @wlunlocker",
            f"# last-update: {today}",
            f"# count: {len(unique_keys)}",
            "",
        ]

        file_content = "\n".join(header) + "\n" + "\n".join(unique_keys)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(file_content)


if __name__ == "__main__":
    asyncio.run(main())
