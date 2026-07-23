import base64
from datetime import datetime
import re
import requests

SUB_URL = "https://sub.67vpn.monster/V4XtpRqVJ8umZbvX?h=6d0065eef10e3dfa"
OUTPUT_FILE = "privateWLunlocker.txt"


def fetch_and_format():
    headers = {
        "User-Agent": "v2rayN/6.23"  # Притворяемся VPN-клиентом, чтобы подписка отдалась без проблем
    }

    try:
        response = requests.get(SUB_URL, headers=headers, timeout=15)
        response.raise_for_status()
        raw_content = response.text.strip()

        try:
            missing_padding = len(raw_content) % 4
            if missing_padding:
                raw_content += "=" * (4 - missing_padding)

            decoded_bytes = base64.b64decode(raw_content)
            content = decoded_bytes.decode("utf-8", errors="ignore")
        except Exception:
            # Если это уже обычный текст без Base64:
            content = raw_content

        keys = re.findall(r"(?:vless|vmess|trojan|ss)://[^\s]+", content)

        unique_keys = list(dict.fromkeys(keys))

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

        print(
            f"Успешно! Обновлено ключей: {len(unique_keys)}, дата: {today}"
        )

    except Exception as e:
        print(f"Ошибка при обновлении подписки: {e}")
        exit(1)


if __name__ == "__main__":
    fetch_and_format()
