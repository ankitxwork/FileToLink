# ✨ Smart Web Stream API

![Smart Web Stream API](https://i.ibb.co/Hh4kF2b/icon.png)

**Smart Web Stream API** is a high-performance, secure API for streaming and downloading Telegram files. Built with **FastAPI** and **Telethon**, it offers low-latency streaming, secure access, and partial downloads. Crafted by **Abir Arafat Chawdhury 🇧🇩**.

**Repository**: [github.com/abirxdhack/FileToLink](https://github.com/abirxdhack/FileToLink)

---

<details>
<summary><b>🚀 Features</b></summary>

- **Telegram Integration** ✨  
  Access Telegram files seamlessly via Telethon.  
- **High-Speed Streaming** 🖥️  
  Stream media with minimal latency and adaptive quality.  
- **Secure Downloads** 🔒  
  Download files with code-based authentication.  
- **Code Authentication** 🔑  
  Protect access with unique, user-specific codes.  
- **Range-Based Downloads** 📏  
  Support partial downloads using HTTP Range headers.  
- **Robust Error Handling** ⚠️  
  Clear error responses for invalid requests (400, 401, 403, 404, 416, 500, 503).

</details>

---

<details>
<summary><b>🛠️ Setup</b></summary>

### Prerequisites
- Python 3.8+
- `pip3`
- `screen`
- Telegram API credentials & bot token
- Telegram channel for logging

### Steps
1. **Clone Repository**  
   ```bash
   git clone https://github.com/abirxdhack/FileToLink.git
   ```

2. **Navigate to Directory**  
   ```bash
   cd FileToLink
   ```

3. **Install Dependencies**  
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Configure API**  
   Edit `config.py`:  
   ```python
   API_ID = YOUR_API_ID
   API_HASH = "YOUR_API_HASH"
   BOT_TOKEN = "YOUR_BOT_TOKEN"
   LOG_CHANNEL_ID = YOUR_CHANNEL_ID
   ```
   - Get `API_ID` & `API_HASH` from [my.telegram.org](https://my.telegram.org).  
   - Create a bot via [BotFather](https://t.me/BotFather) for `BOT_TOKEN`.  
   - Set `LOG_CHANNEL_ID` (e.g., `-1001234567890`). Ensure bot is admin.

5. **Install Screen**  
   ```bash
   apt install screen
   ```

6. **Run API**  
   ```bash
   screen -S FileToLink
   python3 api.py
   ```
   - Detach: `Ctrl+A`, `Ctrl+D`.  
   - Reattach: `screen -r FileToLink`.

7. **Access API**  
   Available at `http://147.93.19.133:8000`. Set `BASE_URL` for custom domains.

</details>

---

<details>
<summary><b>📡 API Endpoints</b></summary>

- **GET /**  
  Returns the API homepage.  
  - **Parameters**: None  
  - **Response**: HTML content  
  - **Example**:  
    ```bash
    curl -X GET "http://147.93.19.133:8000/"
    ```

- **GET /stream/{file_id}**  
  Streams a Telegram file.  
  - **Parameters**:  
    - `file_id` (int): Message ID  
    - `code` (str): Authentication code  
  - **Response**: HTML player  
  - **Example**:  
    ```bash
    curl -X GET "http://147.93.19.133:8000/stream/12345?code=abc123"
    ```

- **GET /dl/{file_id}**  
  Downloads a Telegram file.  
  - **Parameters**:  
    - `file_id` (int): Message ID  
    - `code` (str): Authentication code  
    - `Range` (header, optional): Byte range  
  - **Response**: File stream  
  - **Example**:  
    ```bash
    curl -X GET "http://147.93.19.133:8000/dl/12345?code=abc123" -H "Range: bytes=0-1048575"
    ```

</details>

---

<details>
<summary><b>🤖 API Usage in Telegram Bot</b></summary>

Integrate the API into a Telegram bot to generate stream and download links for files using `/fdl` command.

### Example Code
```python
import asyncio
import secrets
import urllib.parse
from datetime import datetime
from mimetypes import guess_type
from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from pyrogram.enums import ParseMode as SmartParseMode
from pyrogram.types import Message as SmartMessage
from pyrogram.enums import ChatMemberStatus
from bot import dp, SmartPyro
from bot.helpers.utils import new_task
from bot.helpers.botutils import send_message, delete_messages
from bot.helpers.commands import BotCommands
from bot.helpers.logger import LOGGER
from bot.helpers.notify import Smart_Notify
from bot.helpers.buttons import SmartButtons
from bot.helpers.defend import SmartDefender
from config import LOG_CHANNEL_ID
import os

logger = LOGGER
BASE_URL = os.getenv("BASE_URL", "http://147.93.19.133:8000")

async def get_file_properties(message: Message):
    file_name = None
    file_size = 0
    mime_type = None
    resolution = None
    if message.document:
        file_name = message.document.file_name
        file_size = message.document.file_size
        mime_type = message.document.mime_type
    elif message.video:
        file_name = getattr(message.video, 'file_name', None)
        file_size = message.video.file_size
        mime_type = message.video.mime_type
        resolution = f"{message.video.width}x{message.video.height}" if message.video.width and message.video.height else None
    elif message.audio:
        file_name = getattr(message.audio, 'file_name', None)
        file_size = message.audio.file_size
        mime_type = message.audio.mime_type
    elif message.photo:
        file_name = None
        file_size = message.photo[-1].file_size
        mime_type = "image/jpeg"
        resolution = f"{message.photo[-1].width}x{message.photo[-1].height}" if message.photo[-1].width and message.photo[-1].height else None
    elif message.video_note:
        file_name = None
        file_size = message.video_note.file_size
        mime_type = "video/mp4"
    if not file_name:
        attributes = {
            "video": "mp4",
            "audio": "mp3",
            "video_note": "mp4",
            "photo": "jpg",
        }
        for attribute in attributes:
            if getattr(message, attribute, None):
                file_type, file_format = attribute, attributes[attribute]
                break
            else:
                raise ValueError("Invalid media type.")
        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{file_type}-{date}"
        if resolution:
            file_name += f" ({resolution})"
        file_name += f".{file_format}"
    if not mime_type:
        mime_type = guess_type(file_name)[0] or "application/octet-stream"
    return file_name, file_size, mime_type

async def format_file_size(file_size: int):
    if file_size < 1024 * 1024:
        size = file_size / 1024
        unit = "KB"
    elif file_size < 1024 * 1024 * 1024:
        size = file_size / (1024 * 1024)
        unit = "MB"
    else:
        size = file_size / (1024 * 1024 * 1024)
        unit = "GB"
    return f"{size:.2f} {unit}"

async def handle_file_download(message: Message, bot: Bot):
    user_id = message.from_user.id if message.from_user else None
    if not message.reply_to_message:
        await send_message(
            chat_id=message.chat.id,
            text="<b>Please Reply To File For Link</b>",
            parse_mode=ParseMode.HTML
        )
        return
    reply_message = message.reply_to_message
    if not (reply_message.document or reply_message.video or reply_message.photo or reply_message.audio or reply_message.video_note):
        await send_message(
            chat_id=message.chat.id,
            text="<b>Please Reply To A Valid File</b>",
            parse_mode=ParseMode.HTML
        )
        return
    processing_msg = await send_message(
        chat_id=message.chat.id,
        text="<b>Processing Your File...</b>",
        parse_mode=ParseMode.HTML
    )
    try:
        bot_member = await SmartPyro.get_chat_member(LOG_CHANNEL_ID, "me")
        if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await processing_msg.edit_text(
                "<b>Error: Bot must be an admin in the log channel</b>",
                parse_mode=ParseMode.HTML
            )
            return
        code = f"{secrets.token_urlsafe(16)}-{user_id}"
        file_name, file_size, mime_type = await get_file_properties(reply_message)
        file_id = None
        if message.chat.id == LOG_CHANNEL_ID:
            file_id = reply_message.message_id
            sent = await SmartPyro.copy_message(
                chat_id=LOG_CHANNEL_ID,
                from_chat_id=LOG_CHANNEL_ID,
                message_id=reply_message.message_id,
                caption=code,
                parse_mode=SmartParseMode.HTML
            )
            file_id = sent.id
        else:
            sent = await reply_message.forward(LOG_CHANNEL_ID)
            file_id = sent.message_id
            sent = await SmartPyro.copy_message(
                chat_id=LOG_CHANNEL_ID,
                from_chat_id=LOG_CHANNEL_ID,
                message_id=file_id,
                caption=code,
                parse_mode=SmartParseMode.HTML
            )
            file_id = sent.id
        quoted_code = urllib.parse.quote(code)
        base_url = BASE_URL.rstrip('/')
        download_link = f"{base_url}/dl/{file_id}?code={quoted_code}"
        is_video = mime_type.startswith('video') or reply_message.video or reply_message.video_note
        stream_link = f"{base_url}/dl/{file_id}?code={quoted_code}=stream" if is_video else None
        smart_buttons = SmartButtons()
        smart_buttons.button("🚀 Download", url=download_link)
        if stream_link:
            smart_buttons.button("🖥️ Stream", url=stream_link)
        keyboard = smart_buttons.build_menu(b_cols=2)
        response = (
            f"<b>✨ Your Links are Ready! ✨</b>\n\n"
            f"<code>{file_name}</code>\n\n"
            f"<b>📂 File Size:</b> <code>{await format_file_size(file_size)}</code>\n\n"
            f"<b>🚀 Download Link:</b> <code>{download_link}</code>\n\n"
        )
        if stream_link:
            response += f"<b>🖥️ Stream Link:</b> <code>{stream_link}</code>\n\n"
        response += "<b>⌛️ Note: </b>\n<blockquote>Links remain active while the bot is running and the file is accessible.</blockquote>"
        await processing_msg.edit_text(
            text=response,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        logger.info(f"Generated links for file_id: {file_id}, download: {download_link}, stream: {stream_link}")
    except Exception as e:
        logger.error(f"Error generating links for file_id: {file_id if 'file_id' in locals() else 'unknown'}, error: {str(e)}")
        await Smart_Notify(bot, f"{BotCommands}fdl", e, processing_msg)
        await processing_msg.edit_text(
            f"<b>Error: Failed to generate link - {str(e)}</b>",
            parse_mode=ParseMode.HTML
        )

@dp.message(Command(commands=["fdl"], prefix=BotCommands))
@new_task
@SmartDefender
async def fdl_command(message: Message, bot: Bot):
    await handle_file_download(message, bot)
```

### How It Works
- **Trigger**: Use `/fdl` to reply to a file (document, video, photo, audio, video note).  
- **Validation**: Ensures the replied message contains a valid file and the bot is an admin in `LOG_CHANNEL_ID`.  
- **File Processing**: Extracts file name, size, and MIME type; generates a unique code (`secrets.token_urlsafe`).  
- **Link Generation**: Forwards file to `LOG_CHANNEL_ID`, creates download (`/dl/{file_id}?code={code}`) and stream (for videos) links.  
- **Response**: Sends file details with inline buttons for downloading and streaming.  
- **Notes**: Requires `aiogram`, `pyrogram`, and `BASE_URL` set to `http://147.93.19.133:8000`. Links remain active while the bot runs.

</details>

---

<details>
<summary><b>🤝 Contributing</b></summary>

1. Fork [github.com/abirxdhack/FileToLink](https://github.com/abirxdhack/FileToLink).  
2. Create a branch: `git checkout -b feature/YourFeature`.  
3. Commit changes: `git commit -m "Add YourFeature"`.  
4. Push: `git push origin feature/YourFeature`.  
5. Open a pull request.

</details>

---

<details>
<summary><b>📩 Contact</b></summary>

For custom bots or APIs in Python, PHP, Node.js, or more:  
- **Telegram**: [t.me/AbirArafatChawdhury](t.me/ISmartCoder)  
- **GitHub**: [github.com/TheSmartDevs](https://github.com/TheSmartDevs)  
- **Community**: [t.me/TheSmartDev](https://t.me/TheSmartDev)

</details>

---

**License**: MIT License. See [LICENSE](LICENSE).  

**Crafted by [Abir Arafat Chawdhury 🇧🇩](ISmartCoder)**  
© 2025 Smart Web Stream