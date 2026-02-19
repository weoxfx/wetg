

# 🌟 WETG v7 “Super Weox” – One-File Telegram Bot Language

**Write Telegram bots without coding.**
Clone the repo, create a `.wetg` file, run the interpreter — your bot is live instantly!

---

## 🔹 Features

* **Readable, beginner-friendly syntax**
* **Single file interpreter**: `wetg.py`
* Supports:

  * Sending messages (`send`)
  * Asking questions (`ask`)
  * Buttons (`button`)
  * Loops (`loop X times`)
  * If / elif / else
  * Functions (`function / call`)
  * Formatting: `**bold**, *italic*, 'quote'`
  * Bot info: `{bot.name}, {bot.username}, {bot.id}`
  * User info: `{user.name}, {user.username}, {user.id}`
* Warnings instead of crashes
* Works on **Replit**, local Python, or Docker

---

## 🔹 Quick Start

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YourUser/WETG.git
cd WETG
```

### 2️⃣ Create your bot `.wetg` file

* Example: `mybot.wetg`

```wetg
wetg "Super Weox"
import random

bot "YOUR_BOT_TOKEN_HERE"

on /start
  send "Hello {user.name} 👋"
  ask "What's your favorite color?"
  set color = {usermsg}
  send "Wow **{color}** is nice!"
  button = ["Visit Site","https://example.com"]
  send "Click below!" with button

on usermsg
  send "You said: {usermsg}"
```

---

### 3️⃣ Optional: Use `config.txt` for your token

Instead of putting the token in `.wetg`, create a `config.txt`:

```
TOKEN=123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

`wetg.py` will read it automatically.

---

### 4️⃣ Run your bot

```bash
python wetg.py mybot.wetg
```

**Output:**

```
🔥 WETG v7 Super Weox
✅ Registered /start
🚀 WETG Bot Running...
```

Your bot is now **online** and responds to Telegram commands.

---

## 🔹 Example Visual

**User Interaction:**

| User Message | Bot Response                                 |
| ------------ | -------------------------------------------- |
| `/start`     | Hello Weox 👋<br>What's your favorite color? |
| `blue`       | Wow **blue** is nice!<br>[Visit Site Button] |
| `ping`       | You said: ping                               |

**Formatting Demo:**

* `**Bold**` → **Bold**
* `*Italic*` → *Italic*
* `'Quote'` → 'Quote'

---

### 5️⃣ Loops & Functions

```wetg
loop 3 times
  send "Random number: {random.randint(1,100)}"
stop

function greet
  send "Hello {user.name}!"
call greet
```

* `loop X times` repeats messages
* `function / call` lets you reuse code

---

## 🔹 Beginners Tips

* **Always use quotes** for strings: `"Hello"`
* **Variables in strings**: `{variable}`
* **Indent with 2 spaces** for blocks (no `{}`)
* **Ask stores reply**: use `set variable = {usermsg}`

---

## 🔹 Running on Replit

1. Create **Python Replit project**
2. Upload `wetg.py` and your `.wetg` file
3. Click **Run**
4. Your bot is live instantly — no Python knowledge needed

![Replit Example](https://i.imgur.com/3u3Bq3Y.png)

---

## 🔹 Contributing / Adding Examples

* Add new `.wetg` scripts to `examples/` folder
* Make your own bots and share them
* Keep the syntax **simple, readable, beginner-friendly**

---

## 🔹 Requirements

* Python 3.12+
* `python-telegram-bot` library

```bash
pip install python-telegram-bot==20.4
```

---

## 🔹 License

MIT License – Free to use and share!

