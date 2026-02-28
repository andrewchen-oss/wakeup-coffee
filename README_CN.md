# ☕ WakeUp Coffee — Whoop × 饿了么自动点餐

> **醒来即有咖啡，无需动手。**

WakeUp Coffee 监控你的 [Whoop](https://www.whoop.com/) 健康手环，一旦检测到你起床，立刻自动在[饿了么](https://www.ele.me/)帮你下单早咖啡。

不用闹钟，不用摸手机，咖啡自己就来了。

---

## ✨ 演示效果

```
[08:12] Whoop 检测到：新的恢复周期开始
[08:12] 恢复分数: 82 | HRV: 64ms | 静息心率: 52bpm
[08:12] 确认起床 ✓
[08:12] 正在饿了么下单...
[08:12] ✅ 下单成功！冰美式 × 1 — 预计送达 08:34
[08:12] Telegram 通知已发送
```

---

## 🏗 工作原理

```
┌─────────────┐   每30分钟轮询    ┌──────────────────┐
│  Whoop API  │ ────────────────► │  whoop_monitor   │
└─────────────┘                   └────────┬─────────┘
                                           │ 检测到起床
                                           ▼
                                  ┌──────────────────┐
                                  │  morning_coffee  │  ◄── config.json
                                  └────────┬─────────┘
                                           │
                            ┌──────────────┴──────────────┐
                            ▼                             ▼
                  ┌──────────────────┐         ┌──────────────────┐
                  │   eleme_order    │         │  Telegram 通知   │
                  └──────────────────┘         └──────────────────┘
```

---

## 🚀 快速开始

### 1. 克隆 & 安装

```bash
git clone https://github.com/YOUR_USERNAME/wakeup-coffee.git
cd wakeup-coffee
pip install -r requirements.txt
```

### 2. 配置

```bash
cp config/config.example.json config/config.json
# 编辑 config/config.json，填入你的凭证
```

### 3. 运行

```bash
python scripts/morning_coffee.py
```

演示模式（不会真实下单）：

```bash
python scripts/morning_coffee.py --demo
```

---

## ⚙️ 配置说明

编辑 `config/config.json`：

```json
{
  "whoop": {
    "access_token": "你的 Whoop access_token",
    "refresh_token": "你的 Whoop refresh_token",
    "user_id": "你的 Whoop 用户 ID"
  },
  "eleme": {
    "sid": "饿了么 session ID（抓包获取）",
    "device_id": "设备 ID（抓包获取）",
    "shop_id": "常点店铺 ID",
    "item_id": "常点商品 ID",
    "address_id": "收货地址 ID"
  },
  "telegram": {
    "bot_token": "Telegram Bot Token",
    "chat_id": "你的 Chat ID"
  },
  "order": {
    "item_name": "冰美式",
    "delivery_address": "北京市朝阳区...",
    "quiet_hours": ["23:00", "07:00"]
  }
}
```

详细配置见 [docs/setup.md](docs/setup.md)。

---

## 📦 项目结构

```
wakeup-coffee/
├── README.md                   # 英文文档
├── README_CN.md                # 中文文档
├── requirements.txt
├── .gitignore
├── config/
│   └── config.example.json     # 配置模板
├── scripts/
│   ├── morning_coffee.py       # 主流程
│   ├── whoop_monitor.py        # Whoop 起床检测
│   └── eleme_order.py          # 饿了么下单
└── docs/
    └── setup.md                # 详细部署指南
```

---

## 🔑 如何获取凭证

### Whoop Token
参见 [docs/setup.md → Whoop OAuth](docs/setup.md#whoop-oauth)

### 饿了么 Session
使用抓包工具（iOS 推荐 Stream）捕获饿了么 App 请求中的 `sid` 和 `device_id`。
参见 [docs/setup.md → 获取饿了么凭证](docs/setup.md#eleme-credentials)

---

## 🛡 隐私与安全

- **不要把 `config/config.json` 上传 GitHub** — 已加入 `.gitignore`
- 凭证仅本地存储，不上传任何第三方服务

---

## 🗺 计划功能

- [x] Whoop 起床检测
- [x] 饿了么自动下单
- [x] Telegram 通知
- [ ] 多店铺轮换
- [ ] 根据恢复分数智能选品
- [ ] iOS 快捷指令集成（备用方案）
- [ ] Web 管理面板

---

## 📄 开源协议

MIT — 随便用。

---

*用 ☕ 和对自动化的热爱构建。*
