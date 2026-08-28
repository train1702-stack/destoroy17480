#!/usr/bin/env python3
"""
指定ページのスクリーンショットを撮影し、Discordの Webhook に投稿するスクリプト。
2時間ごとに実行したい場合は、このスクリプト自体をループさせるのではなく、
cron（または Windows のタスクスケジューラ）から「1回だけ実行」するように登録してください。
その方が、PCの再起動やエラーで落ちても次の実行で自動的に復帰するので安定します。

必要なライブラリ:
    pip install playwright requests
    playwright install chromium

環境変数:
    DISCORD_WEBHOOK_URL  Discordの Webhook URL（必須）
"""

import os
import sys
from datetime import datetime

import requests
from playwright.sync_api import sync_playwright

# ==== 設定 ====
TARGET_URL = "https://www.kataller.co.jp/sponsor-top/train/"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
VIEWPORT = {"width": 1280, "height": 900}
TIMEOUT_MS = 30_000  # ページ読み込みのタイムアウト（30秒）


def take_screenshot() -> str:
    """ページ全体のスクリーンショットを撮影し、保存先パスを返す"""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SCREENSHOT_DIR, f"screenshot_{timestamp}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT)
        page.goto(TARGET_URL, wait_until="networkidle", timeout=TIMEOUT_MS)
        page.screenshot(path=path, full_page=True)
        browser.close()

    return path


def send_to_discord(image_path: str) -> None:
    """撮影した画像をDiscordのWebhookに送信する"""
    if not WEBHOOK_URL:
        raise RuntimeError(
            "環境変数 DISCORD_WEBHOOK_URL が設定されていません。"
        )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"📸 スクリーンショット取得: {TARGET_URL}\n({timestamp})"

    with open(image_path, "rb") as f:
        files = {"file": (os.path.basename(image_path), f, "image/png")}
        data = {"content": content}
        resp = requests.post(WEBHOOK_URL, data=data, files=files, timeout=30)
        resp.raise_for_status()


def main() -> int:
    try:
        path = take_screenshot()
        print(f"[OK] スクリーンショット保存: {path}")
        send_to_discord(path)
        print("[OK] Discordへの投稿完了")
        return 0
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
