# ☕ WakeUp Coffee — Whoop × Ele.me Auto-Order

> **Wake up. Coffee ordered. Magic.**

WakeUp Coffee monitors your [Whoop](https://www.whoop.com/) health tracker and automatically orders your morning coffee on [Ele.me](https://www.ele.me/) the moment it detects you've woken up.

No alarm. No fumbling with your phone. Coffee just... arrives.

---

## ✨ Demo

```
[08:12] Whoop detected: New recovery cycle started
[08:12] Recovery score: 82 | HRV: 64ms | RHR: 52bpm
[08:12] Wake-up confirmed ✓
[08:12] Placing order on Ele.me...
[08:12] ✅ Order placed! Iced Americano × 1 — ETA 08:34
[08:12] Notification sent to Telegram
```

---

## 🏗 How It Works

```
┌─────────────┐     poll every      ┌──────────────────┐
│  Whoop API  │ ──── 30 minutes ──► │  whoop_monitor   │
└─────────────┘                     └────────┬─────────┘
                                             │ wake detected
                                             ▼
                                    ┌──────────────────┐
                                    │  morning_coffee  │  ◄── config.json
                                    └────────┬─────────┘
                                             │
                              ┌──────────────┴──────────────┐
                              ▼                             ▼
                    ┌──────────────────┐         ┌──────────────────┐
                    │   eleme_order    │         │ Telegram notify  │
                    └──────────────────┘         └──────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/wakeup-coffee.git
cd wakeup-coffee
pip install -r requirements.txt
```

### 2. Configure

```bash
cp config/config.example.json config/config.json
# Edit config/config.json with your credentials
```

### 3. Run

```bash
python scripts/morning_coffee.py
```

Or run in demo mode (no real orders placed):

```bash
python scripts/morning_coffee.py --demo
```

---

## ⚙️ Configuration

Edit `config/config.json`:

```json
{
  "whoop": {
    "access_token": "YOUR_WHOOP_ACCESS_TOKEN",
    "refresh_token": "YOUR_WHOOP_REFRESH_TOKEN",
    "user_id": "YOUR_WHOOP_USER_ID"
  },
  "eleme": {
    "sid": "YOUR_ELEME_SESSION_ID",
    "device_id": "YOUR_DEVICE_ID",
    "shop_id": "YOUR_FAVORITE_SHOP_ID",
    "item_id": "YOUR_FAVORITE_ITEM_ID",
    "address_id": "YOUR_DELIVERY_ADDRESS_ID"
  },
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  },
  "order": {
    "item_name": "冰美式",
    "delivery_address": "北京市朝阳区...",
    "quiet_hours": ["23:00", "07:00"]
  }
}
```

See [docs/setup.md](docs/setup.md) for a full setup guide.

---

## 📦 Project Structure

```
wakeup-coffee/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   └── config.example.json     # Config template
├── scripts/
│   ├── morning_coffee.py       # Main orchestrator
│   ├── whoop_monitor.py        # Whoop wake detection
│   └── eleme_order.py          # Ele.me ordering
└── docs/
    └── setup.md                # Full setup guide
```

---

## 🔑 Getting Your Credentials

### Whoop Token
See [docs/setup.md → Whoop OAuth](docs/setup.md#whoop-oauth)

### Ele.me Session
Use a packet capture tool (e.g., Stream on iOS) to capture your `sid` and `device_id` from the Ele.me app.
See [docs/setup.md → Capturing Ele.me Credentials](docs/setup.md#eleme-credentials)

---

## 🛡 Privacy & Security

- **Never commit `config/config.json`** — it's in `.gitignore`
- Credentials are stored locally only
- No data is sent to any third-party service

---

## 🗺 Roadmap

- [x] Whoop wake detection
- [x] Ele.me order placement
- [x] Telegram notification
- [ ] Support multiple coffee shops (rotation)
- [ ] Smart ordering based on recovery score
- [ ] iOS Shortcut integration as fallback
- [ ] Web dashboard

---

## 📄 License

MIT — do whatever you want with it.

---

*Built with ☕ and a love for automation.*
