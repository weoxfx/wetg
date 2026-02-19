# 🔥 WETG v7 — Super Weox

> **One-File Telegram Bot Engine** — Write Telegram bots in a simple scripting language, no boilerplate needed.

---

## 📦 Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

> On Termux / system Python (no virtualenv):
> ```bash
> pip install -r requirements.txt --break-system-packages
> ```

### 2. Make the launcher executable

```bash
chmod +x wetg.sh
```

### 3. (Optional) Add `wetg` to your PATH

```bash
# Termux
cp wetg.sh $PREFIX/bin/wetg

# Linux / macOS
sudo cp wetg.sh /usr/local/bin/wetg
```

Now you can run `wetg` from anywhere.

---

## 🚀 Quick Start

```bash
# Create a new bot from template
wetg new mybot.wetg

# Edit the file and add your token from @BotFather
nano mybot.wetg

# Run it
wetg run mybot.wetg
```

---

## 📝 WETG Language Reference

### Bot Token

```
bot "123456789:ABC-your-token-here"
```

Or put it in `config.txt` (safer, don't commit to git):

```
TOKEN=123456789:ABC-your-token-here
```

---

### Commands

Register a Telegram `/command`:

```
on /start
    send "Hello, {user.name}!"

on /ping
    send "🏓 Pong!"
```

---

### Sending Messages

```
send "Hello!"
send "Hi {user.name}, your ID is {user.id}"

# With Markdown formatting
send "*bold* and _italic_" with markdown

# With HTML formatting
send "<b>bold</b>" with html

# With an inline button
button = ["Click me", "https://example.com"]
send "Check this out!" with button

# With an image (local file or URL)
send "photo.jpg" with image
send "https://example.com/image.jpg" with image
```

---

### Variables

```
set greeting=Hello there

on /start
    send "{greeting}, {user.name}!"
```

---

### Asking Questions

```
on /echo
    ask "What should I repeat?"

on usermsg
    send "You said: {usermsg}"
```

> After `ask`, the bot waits for the user's next message and stores it in `{usermsg}`.

---

### Handling User Messages

```
on usermsg
    if {usermsg} == "hi"
        send "Hey! 👋"
    elif {usermsg} == "bye"
        send "See ya! 👋"
    else
        send "I got: {usermsg}"
```

---

### Loops

```
on /count
    loop 3 times
        send "Counting..."
    stop
```

---

### Functions

```
function greet
    send "Hi {user.name}!"
    send "Welcome to the bot."

on /start
    call greet
```

---

### Imports

```
import random

on /roll
    send "🎲 You rolled a {random.randint(1, 6)}!"
```

---

## 🔤 Available Variables

| Variable | Description |
|---|---|
| `{user.name}` | User's first name |
| `{user.id}` | User's Telegram ID |
| `{user.username}` | User's @username |
| `{bot.name}` | Bot's display name |
| `{bot.username}` | Bot's @username |
| `{usermsg}` | Last message text sent by user |

---

## 🛠 CLI Reference

```
wetg run <file.wetg>     Run a bot
wetg new <file.wetg>     Create a bot from template
wetg check <file.wetg>   Validate your .wetg file
wetg version             Show WETG version
wetg help                Show help
```

Shortcuts:

```bash
# These are equivalent
wetg run mybot.wetg
wetg mybot.wetg
python wetg.py mybot.wetg
python wetg.py run mybot.wetg
```

---

## 📁 Project Structure

```
wetg/
├── wetg.py           # The interpreter
├── wetg.sh           # CLI launcher (wetg command)
├── requirements.txt  # Python dependencies
├── example.wetg      # Example bot
├── config.txt        # (optional) TOKEN=... — don't commit this!
└── README.md
```

---

## 🔒 Security Tips

- Never hardcode your token in `.wetg` files you share or commit to git.
- Use `config.txt` for your token and add it to `.gitignore`:
  ```
  config.txt
  .env
  ```

---

## 📋 Example Bot

```
bot "YOUR_TOKEN"

set welcome=Hello!

on /start
    send "👋 Hi {user.name}! {welcome}"

on /ping
    send "🏓 Pong!"

on /echo
    ask "What should I echo?"

on usermsg
    send "Echo: {usermsg}"
```

---

## 🐛 Troubleshooting

**`RuntimeError: This event loop is already running`**
Fixed in v7 — WETG now uses the low-level async API instead of `run_polling()`.

**`python-telegram-bot` version issues**
Make sure you have v20+: `pip install "python-telegram-bot>=20.0"`

**Bot not responding**
Run `wetg check mybot.wetg` to validate your file, and make sure your token is correct.

---

## 📜 License

MIT — do whatever you want with it.
