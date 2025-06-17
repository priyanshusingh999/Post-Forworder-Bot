# 🤖 Post Forwarder Telegram Bot

A simple but powerful Telegram bot that **automatically forwards any message you send to your selected Telegram channels**.

Made with 💙 using pure Python + Requests + Flask. No extra frameworks, easy to deploy anywhere — **Render** and **Koyeb** supported.

---

## ✨ Features

- ✅ Forwards text, media, files — everything!
- ➕ Add/remove multiple channels per user
- 🔐 Admin-only commands (`/broadcast`, `/users`)
- 🚫 Optional force-join a channel before use
- 💾 Uses MongoDB for storing user data and toggles
- ☁️ Runs on free hosting platforms like **Render** or **Koyeb**
- 📸 Supports media group forwarding with links
- 🔁 Toggle post URL display and getChat response per user

---

## 🚀 One-Click Deploy

Deploy for free with one click:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?...)

---

## ⚙️ Environment Variables

| Variable Name       | Required | Description                                          |
|---------------------|----------|------------------------------------------------------|
| `TOKEN`             | ✅       | Telegram bot token from BotFather                    |
| `OWNER_ID`          | ✅       | Your numeric Telegram user ID                        |
| `MONGO_URI`         | ✅       | MongoDB connection URI                               |
| `DB_NAME`           | ❌       | MongoDB database name (default: `postforworder`)    |
| `FORCE_SUB_CHANNEL` | ❌       | Channel username (e.g. `@mychannel`) to force-join   |

📝 Example (`.env` or Render Environment Settings):

```
TOKEN=123456789:ABCDEF...
OWNER_ID=123456789
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net
DB_NAME=postforworder
FORCE_SUB_CHANNEL=@mychannel
```

---

## 🧪 Usage Guide

1. **Start the bot** on Telegram:  
   Send `/start` to begin.

2. **Add channels** (must be full `channel_id`, e.g. `-1001234567890`):  
   Use `/addchannel <channel_id1> <channel_id2> ...` to add one or more channels.

3. **Remove channels**:  
   Use `/removechannel <channel_id1> <channel_id2> ...` to remove channels.

4. **Forward any message** (text/photo/video/file) — the bot will send it to all your added channels.

5. **Check your added channels**:  
   Use `/mychannels` to list your currently added channels.

> ⚠️ Bot must be an **admin** in all your added channels.

---

## 📜 Total Bot Commands

### 👤 User Commands (for everyone)
| Command               | Description                                  |
|-----------------------|----------------------------------------------|
| `/start`              | Start the bot / see welcome message          |
| `/addchannel <ids>`   | Add one or more channel IDs                  |
| `/removechannel <ids>`| Remove one or more channel IDs                |
| `/mychannels`         | List your currently added channels           |
| `/toggleurls`         | Toggle showing post URLs ON/OFF               |
| `/togglegetchat`      | Toggle responding to `/getChat` command       |
| `/getChat`            | Show raw update JSON (if `/togglegetchat` ON)|

### 👑 Owner Commands (only for `OWNER_ID`)
| Command                | Description                              |
|------------------------|------------------------------------------|
| `/users`               | Show total users using the bot           |
| `/broadcast <message>` | Send a message to all users              |

---

## 🙌 Credits
Made by [@priyanshusingh999](https://github.com/priyanshusingh999)

Want to customize or upgrade this bot? Feel free to fork!
