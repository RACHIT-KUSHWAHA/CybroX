<h1 align="center">
    <img src="https://telegra.ph/file/7c04400508a8677bf9432.jpg" alt="CybroX Logo" width="200">
    <br>
    <b>CybroX Userbot</b>
</h1>

<p align="center">
    <a href="https://github.com/RACHIT-KUSHWAHA/CybroX/stargazers"><img src="https://img.shields.io/github/stars/RACHIT-KUSHWAHA/CybroX?color=yellow&logo=github&style=for-the-badge" alt="Stars" /></a>
    <a href="https://github.com/RACHIT-KUSHWAHA/CybroX/network/members"><img src="https://img.shields.io/github/forks/RACHIT-KUSHWAHA/CybroX?color=red&logo=github&style=for-the-badge" alt="Forks" /></a> 
    <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&style=for-the-badge" alt="Python" /></a>
    <a href="https://docs.pyrogram.org"><img src="https://img.shields.io/badge/Pyrogram-v2-orange?logo=telegram&style=for-the-badge" alt="Pyrogram" /></a>
</p>

<p align="center">
  <b>Advanced. Lightweight. Zero-Cost.</b><br>
  CybroX is a next-generation Telegram Userbot optimized for speed, AI capabilities, and free hosting platforms.
</p>

<hr>

## 🌟 Features

| 🛡️ Security | 🧠 Intelligence | 🎬 Media |
| :--- | :--- | :--- |
| **Federation Bans**: Global ban system across all your groups. | **Gemini AI**: Chat with Google's advanced AI directly. | **YT-DLP**: High-Quality Video & Audio downloads. |
| **Sentinel**: VirusTotal malware scanning for files. | **RAG Memory**: Context-aware answers based on chat history. | **Spotify**: Download tracks instantly. |
| **Forensics**: Log edited messages in PMs. | **Smart Assist**: Auto-reply and helper tools. | **Gallery**: Media management tools. |

| 👻 Ghost Mode | ⚡ Performance | 🛠️ Tools |
| :--- | :--- | :--- |
| **Shadow Inbox**: Read messages without "Seen" receipts. | **Zero-Cost**: Runs on free tier hosting (Render/Koyeb). | **OmniKang**: Auto-detect stickers/video packs. |
| **Peek**: View chats secretly. | **Async**: Built on Pyrogram for blazing speed. | **Fun**: Memes, Games, and Generators. |

<hr>

## 🚀 Deployment

<p align="center">
    <a href="https://heroku.com/deploy">
        <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku" width="200" />
    </a>
    <a href="https://render.com/deploy?repo=https://github.com/RACHIT-KUSHWAHA/CybroX">
        <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render" width="200" />
    </a>
    <a href="https://app.koyeb.com/deploy?type=git&repository=RACHIT-KUSHWAHA/CybroX&branch=main&name=cybrox">
        <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy to Koyeb" width="200" />
    </a>
</p>

## 🛠️ Local Setup

Easy setup for developers and local testing.

```bash
# 1. Clone Repository
git clone https://github.com/RACHIT-KUSHWAHA/CybroX.git
cd CybroX

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Configure
# Rename sample.env to .env and fill in your details
cp sample.env .env

# 4. Run
python main.py
```

## ⚙️ Configuration (.env)

| Variable | Description | Required |
| :--- | :--- | :--- |
| `API_ID` | Telegram API ID (my.telegram.org) | ✅ |
| `API_HASH` | Telegram API Hash | ✅ |
| `SESSION_STRING` | Pyrogram Session String | ✅ |
| `SUDO_USERS` | Space-separated IDs of sudo users | ❌ |
| `GEMINI_API_KEY` | Google AI Studio Key (For AI) | ❌ |
| `OPENAI_API_KEY` | OpenAI API Key (For GPT-4o) | ❌ |
| `VT_API_KEY` | VirusTotal Key (For Sentinel) | ❌ |

## 🏗️ Structure

- `userbot/plugins/`: Contains all 50+ modules.
- `userbot/database/`: SQLite3 engine (CybroDB).
- `userbot/helpers/`: Utility functions.

## 🤝 Credits

- **[Pyrogram](https://github.com/pyrogram/pyrogram)**: The foundation.

## 📄 License

This project is licensed under the [GNU General Public License v3.0](LICENSE).