# Setup Guide

Complete guide to deploying WakeUp Coffee.

---

## Prerequisites

- Python 3.8+
- A Whoop health tracker
- An Ele.me account with a saved order and delivery address
- A Telegram bot (for notifications)
- iOS device with a packet capture app (Stream recommended)

---

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 2: Whoop OAuth Setup {#whoop-oauth}

### Get Your Whoop API Credentials

1. Go to [https://developer.whoop.com](https://developer.whoop.com)
2. Create an app → get `client_id` and `client_secret`
3. Set redirect URI to `https://httpbin.org/get`

### Get Your Access Token

Visit this URL in your browser (replace `YOUR_CLIENT_ID`):

```
https://api.prod.whoop.com/oauth/oauth2/auth
  ?response_type=code
  &client_id=YOUR_CLIENT_ID
  &redirect_uri=https://httpbin.org/get
  &scope=offline read:recovery read:cycles
```

After login, you'll be redirected to httpbin — grab the `code` from the URL.

Then exchange the code for a token:

```bash
curl -X POST https://api.prod.whoop.com/oauth/oauth2/token \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=https://httpbin.org/get"
```

Copy `access_token` and `refresh_token` into `config/config.json`.

---

## Step 3: Capturing Ele.me Credentials {#eleme-credentials}

You need to capture your Ele.me session using a packet capture tool.

### Setup Stream (iOS)

1. Install **Stream** from the App Store
2. Open Stream → install the HTTPS certificate (Settings → Trust CA)
3. Start capturing
4. Open the Ele.me app and browse to your favorite item

### What to Capture

Look for requests to `amdc.m.ele.me`. In the request body, find:

| Parameter | Where | Example |
|-----------|-------|---------|
| `sid` | Request body | `2214050594815` |
| `deviceId` | Request body | `Z8iqW21L09sDAP6huZYQyTb2` |

### Get Shop ID & Item ID

While on the restaurant page in Ele.me, look for requests to `restapi.ele.me` — the shop ID and item IDs will be in the URL or response body.

Alternatively, open Ele.me in a browser — the URL usually contains the shop/item IDs.

### Get Address ID

In the order confirmation flow, capture the request that includes your delivery address — it will contain your `address_id`.

---

## Step 4: Telegram Bot Setup

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Run `/newbot` and follow the prompts
3. Copy the bot token into `config/config.json`
4. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)

---

## Step 5: Fill in Config

```bash
cp config/config.example.json config/config.json
```

Edit `config/config.json` with all your credentials.

---

## Step 6: Test

### Test Whoop connection:

```bash
python scripts/whoop_monitor.py
```

### Test demo order (no real order placed):

```bash
python scripts/morning_coffee.py --demo --once
```

### Go live:

```bash
python scripts/morning_coffee.py
```

---

## Running as a Background Service

### macOS (launchd)

Create `~/Library/LaunchAgents/com.wakeup-coffee.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "...">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.wakeup-coffee</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/path/to/wakeup-coffee/scripts/morning_coffee.py</string>
  </array>
  <key>WorkingDirectory</key>
  <string>/path/to/wakeup-coffee</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.wakeup-coffee.plist
```

### Linux (systemd)

```ini
[Unit]
Description=WakeUp Coffee

[Service]
ExecStart=/usr/bin/python3 /path/to/morning_coffee.py
WorkingDirectory=/path/to/wakeup-coffee
Restart=always

[Install]
WantedBy=multi-user.target
```

### Cron (simple alternative)

```bash
# Check every 30 minutes
*/30 * * * * cd /path/to/wakeup-coffee && python3 scripts/morning_coffee.py --once
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Whoop 401 error | Token expired — re-run OAuth flow |
| Ele.me order fails | `sid` may have expired — re-capture from app |
| Telegram not sending | Check bot token and that you've messaged the bot first |
| Wake-up not detected | Check `state.json` — delete it to reset |

---

## Security Notes

⚠️ `config/config.json` contains sensitive credentials. It is in `.gitignore` and will **not** be committed. Keep it local only.
