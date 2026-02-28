"""
morning_coffee.py
-----------------
Main orchestrator: polls Whoop, detects wake-up, orders coffee, notifies via Telegram.

Usage:
  python scripts/morning_coffee.py              # Normal mode
  python scripts/morning_coffee.py --demo       # Demo mode (no real orders)
  python scripts/morning_coffee.py --once       # Check once and exit
"""

import json
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime

# Add parent dir for imports
sys.path.insert(0, "scripts")
from whoop_monitor import check_wake_up, format_recovery_summary
from eleme_order import order_coffee

POLL_INTERVAL_SECONDS = 30 * 60  # 30 minutes


def load_config():
    with open("config/config.json") as f:
        return json.load(f)


def send_telegram(config, message):
    """Send a Telegram notification."""
    bot_token = config["telegram"]["bot_token"]
    chat_id = config["telegram"]["chat_id"]
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"[telegram] Failed to send: {e}")
        return None


def is_quiet_hours(config):
    """Return True if current time is within quiet hours (no ordering)."""
    now = datetime.now().strftime("%H:%M")
    start = config["order"].get("quiet_hours_start", "23:00")
    end = config["order"].get("quiet_hours_end", "07:00")
    if start < end:
        return start <= now < end
    else:  # overnight quiet period
        return now >= start or now < end


def format_success_message(recovery_summary, order_result):
    """Build the Telegram notification message."""
    now = datetime.now()
    eta_minutes = order_result.get("estimated_delivery_minutes", 30)
    eta_time = datetime.now().replace(
        minute=(now.minute + eta_minutes) % 60,
        hour=now.hour + (now.minute + eta_minutes) // 60
    ).strftime("%H:%M")

    score = recovery_summary.get("recovery_score", "N/A")
    hrv = recovery_summary.get("hrv_rmssd_milli", "N/A")
    rhr = recovery_summary.get("resting_heart_rate", "N/A")
    price = order_result.get("total_price", "N/A")
    item = order_result.get("item_name", "咖啡")
    order_id = order_result.get("order_id", "N/A")

    return (
        f"☀️ *早安！检测到你醒啦～*\n\n"
        f"📊 今日恢复数据\n"
        f"  恢复分数：{score}/100\n"
        f"  HRV：{hrv} ms\n"
        f"  静息心率：{rhr} bpm\n\n"
        f"✅ *下单成功！*\n"
        f"  {item} × 1\n"
        f"  实付：¥{price}\n"
        f"  预计送达：{eta_time}\n"
        f"  订单号：`{order_id}`\n\n"
        f"去洗漱吧，咖啡在路上了 🐾"
    )


def run(demo=False, once=False):
    print(f"[main] WakeUp Coffee started {'(DEMO MODE)' if demo else ''}")
    print(f"[main] Poll interval: {POLL_INTERVAL_SECONDS // 60} minutes")

    ordered_today = None

    while True:
        config = load_config()
        today = datetime.now().strftime("%Y-%m-%d")

        # Reset daily order flag
        if ordered_today != today:
            ordered_today = None

        try:
            print(f"[main] [{datetime.now().strftime('%H:%M')}] Checking Whoop...")

            recovery = check_wake_up(config)

            if recovery and ordered_today != today:
                print("[main] Wake-up detected!")
                summary = format_recovery_summary(recovery)
                print(f"[main] Recovery: {summary}")

                if is_quiet_hours(config) and not demo:
                    print("[main] Quiet hours — skipping order.")
                else:
                    order_result = order_coffee(config, demo=demo)
                    print(f"[main] Order result: {order_result}")

                    msg = format_success_message(summary, order_result)
                    send_telegram(config, msg)
                    print("[main] Telegram notification sent ✓")

                    ordered_today = today

            else:
                if ordered_today == today:
                    print("[main] Already ordered today, skipping.")
                else:
                    print("[main] No wake-up event yet.")

        except Exception as e:
            print(f"[main] Error: {e}")
            send_telegram(config, f"⚠️ WakeUp Coffee error: {e}")

        if once:
            break

        print(f"[main] Sleeping {POLL_INTERVAL_SECONDS // 60} minutes...\n")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    demo_mode = "--demo" in sys.argv
    once_mode = "--once" in sys.argv
    run(demo=demo_mode, once=once_mode)
