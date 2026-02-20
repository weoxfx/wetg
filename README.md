# 🔥 WETG v7 — Super Weox

> **One-File Telegram Bot Engine** — Write Telegram bots in a simple scripting language. No boilerplate. No classes. Just write.

```
pip install wetg
```

---

## ⚡ Quick Start

```bash
# Create a bot from template
wetg new mybot.wetg

# Edit it, add your token from @BotFather
nano mybot.wetg

# Run it
wetg run mybot.wetg
```

That's it.

---

## 📝 Language

### Hello World bot

```
bot "YOUR_TOKEN_HERE"

on /start
    send "Hello, {user.name}! 👋"

on /ping
    send "🏓 Pong!"
```

### Full feature example

```
bot "YOUR_TOKEN_HERE"

set welcome=Hello!

# ── Commands ──────────────────────────────

on /start
    send "👋 Hi {user.name}! {welcome}"

on /help
    send "/start\n/ping\n/echo\n/about"

on /ping
    send "🏓 Pong!"

on /about
    button = ["Our Website", "https://example.com"]
    send "Powered by WETG v7 Super Weox." with button

on /echo
    ask "What should I echo?"

# ── User messages ─────────────────────────

on usermsg
    if {usermsg} == "hi"
        send "Hey! 👋"
    elif {usermsg} == "bye"
        send "See ya! 👋"
    else
        send "You said: {usermsg}"

# ── Functions ─────────────────────────────

function welcome_user
    send "Welcome, {user.name}!"
    send "Your ID: {user.id}"
```

---

## 📖 Language Reference

### Token

```
bot "YOUR_TOKEN"
```

Or use `config.txt` (recommended — don't commit tokens to git):
```
TOKEN=YOUR_TOKEN
```

### Sending messages

| Syntax | Description |
|--------|-------------|
| `send "text"` | Plain message |
| `send "{user.name}"` | With variable interpolation |
| `send "**bold**" with markdown` | Markdown formatting |
| `send "<b>bold</b>" with html` | HTML formatting |
| `send "photo.jpg" with image` | Local image file |
| `send "https://..." with image` | Image from URL |
| `button = ["Label", "url"]` then `send "text" with button` | Inline button |

### Variables

| Variable | Value |
|----------|-------|
| `{user.name}` | User's first name |
| `{user.id}` | User's Telegram ID |
| `{user.username}` | User's @username |
| `{bot.name}` | Bot display name |
| `{bot.username}` | Bot @username |
| `{usermsg}` | Last message text from user |

### Control flow

```
if {usermsg} == "yes"
    send "You said yes!"
elif {usermsg} == "no"
    send "You said no."
else
    send "You said something else."
```

### Loops

```
loop 5 times
    send "Looping!"
stop
```

### Ask / input

```
on /form
    ask "What's your name?"

on usermsg
    send "Nice to meet you, {usermsg}!"
```

### Functions

```
function greet
    send "Hi {user.name}!"

on /start
    call greet
```

### Variables (set)

```
set counter=0

on /start
    set counter=1
    send "Counter is {counter}"
```

### Imports

```
import random

on /roll
    send "🎲 {random.randint(1, 6)}"
```

---

## 🐍 Python API

```python
from wetg_superweox import Wetg
import asyncio

code = """
bot "YOUR_TOKEN"

on /start
    send "Hello from Python API!"
"""

bot = Wetg(code)
bot.parse()
asyncio.run(bot.run())
```

Or use the helper:

```python
from wetg_superweox import run_file

run_file("mybot.wetg")
```

---

## 🛠 CLI

```
wetg run <file.wetg>     Run a bot
wetg new <file.wetg>     Create bot from template
wetg check <file.wetg>   Validate .wetg file
wetg version             Show version
wetg help                Show help
```

Shortcuts:
```bash
wetg mybot.wetg           # same as: wetg run mybot.wetg
python -m wetg_superweox run mybot.wetg
```

---

## 🔒 Tips

- Store tokens in `config.txt`, not in `.wetg` files
- Add to `.gitignore`:
  ```
  config.txt
  .env
  ```

---

## 📜 License

MIT