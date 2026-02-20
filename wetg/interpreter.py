"""
WETG v7 "Super Weox" — Interpreter core
"""

import asyncio
import random
import os

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)


# ------------------ USER & BOT INFO ------------------

class User:
    def __init__(self, tg_user):
        self.id = tg_user.id
        self.name = tg_user.first_name
        self.username = tg_user.username or ""

    def __format__(self, spec):
        return self.name


class BotInfo:
    def __init__(self, bot):
        self.id = bot.id
        self.username = bot.username
        self.name = bot.first_name

    def __format__(self, spec):
        return self.name


# ------------------ WETG INTERPRETER ------------------

class Wetg:
    """
    WETG interpreter. Parses and runs .wetg bot scripts.

    Usage (Python API):
        from wetg import Wetg

        with open("mybot.wetg") as f:
            code = f.read()

        bot = Wetg(code)
        bot.parse()

        import asyncio
        asyncio.run(bot.run())
    """

    VERSION = "7"
    VERSION_HEADER = "Super Weox"

    def __init__(self, code: str):
        self.code = code.splitlines()
        self.token = None
        self.commands = {}
        self.usermsg_blocks = []
        self.variables = {}
        self.asking = {}
        self.functions = {}
        self.imports = {}

    # ------------------ PARSER ------------------

    def parse(self):
        """Parse the .wetg source code into an internal command/block structure."""
        current_cmd = None
        current_block = []
        is_usermsg = False
        current_function = None
        function_block = []

        for line in self.code:
            if not line.strip() or line.strip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            stripped = line.strip()

            if stripped.startswith("wetg "):
                continue
            if stripped.startswith("import "):
                for m in stripped[7:].split(","):
                    m = m.strip()
                    try:
                        self.imports[m] = __import__(m)
                    except Exception:
                        print(f"⚠️  Failed to import: {m}")
                continue
            if stripped.startswith("bot "):
                try:
                    self.token = stripped.split('"')[1]
                except Exception:
                    pass
                continue
            if stripped.startswith("function "):
                if current_function:
                    self.functions[current_function] = function_block
                current_function = stripped[9:].strip()
                function_block = []
                continue
            if stripped.startswith("set "):
                try:
                    key, val = stripped[4:].split("=", 1)
                    self.variables[key.strip()] = val.strip()
                except Exception:
                    print(f"⚠️  Invalid set: {stripped}")
                continue
            if stripped.startswith("on "):
                if current_cmd:
                    if is_usermsg:
                        self.usermsg_blocks.append(current_block)
                    else:
                        self.commands[current_cmd] = current_block
                current_cmd = stripped[3:].strip()
                current_block = []
                is_usermsg = (current_cmd == "usermsg")
                continue

            if current_function:
                function_block.append((indent, stripped))
            else:
                current_block.append((indent, stripped))

        if current_function:
            self.functions[current_function] = function_block
        if current_cmd:
            if is_usermsg:
                self.usermsg_blocks.append(current_block)
            else:
                self.commands[current_cmd] = current_block

    # ------------------ BLOCK RUNNER ------------------

    async def run_block(
        self,
        block: list,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        """Execute a parsed block of WETG instructions."""
        user = User(update.effective_user)
        botinfo = BotInfo(context.bot)
        local_vars = self.variables.copy()
        local_vars.update({
            "user": user,
            "bot": botinfo,
            "msg": update.message,
            "usermsg": update.message.text if update.message else "",
            "random": random,
            **self.imports,
        })

        i = 0
        loop_stack = []

        while i < len(block):
            indent, line = block[i]

            try:
                # --- ask ---
                if line.startswith("ask "):
                    q = line[4:].strip().strip('"')
                    try:
                        q = q.format(**local_vars)
                    except Exception:
                        pass
                    await update.message.reply_text(q)
                    self.asking[update.effective_user.id] = True
                    return

                # --- send ... with ... ---
                elif line.startswith("send ") and " with " in line:
                    parts = line.split(" with ", 1)
                    text = parts[0][5:].strip().strip('"')
                    send_type = parts[1].strip()
                    try:
                        text = text.format(**local_vars)
                    except Exception:
                        pass

                    if send_type == "button":
                        keyboard = None
                        for j in range(i - 1, -1, -1):
                            if block[j][1].startswith("button ="):
                                btn_part = block[j][1].split("=", 1)[1].strip()
                                try:
                                    btn_label, btn_url = (
                                        btn_part.strip("[]").replace('"', "").split(",", 1)
                                    )
                                    keyboard = InlineKeyboardMarkup([[
                                        InlineKeyboardButton(
                                            btn_label.strip(), url=btn_url.strip()
                                        )
                                    ]])
                                except Exception:
                                    pass
                                break
                        await update.message.reply_text(text, reply_markup=keyboard)

                    elif send_type == "image":
                        try:
                            if text.startswith("http"):
                                await update.message.reply_photo(text)
                            else:
                                with open(text, "rb") as img:
                                    await update.message.reply_photo(img)
                        except Exception as e:
                            await update.message.reply_text(f"⚠️ Cannot send image: {e}")

                    elif send_type == "markdown":
                        await update.message.reply_text(text, parse_mode="Markdown")

                    elif send_type == "html":
                        await update.message.reply_text(text, parse_mode="HTML")

                # --- send ---
                elif line.startswith("send "):
                    text = line[5:].strip().strip('"')
                    try:
                        text = text.format(**local_vars)
                    except Exception:
                        pass
                    await update.message.reply_text(text)

                # --- loop ---
                elif line.startswith("loop "):
                    parts = line[5:].split()
                    try:
                        times = int(parts[0]) if "times" in parts else int(local_vars.get(parts[0], 0))
                    except Exception:
                        times = 0
                    loop_stack.append((i, times))
                    i += 1
                    continue

                # --- stop ---
                elif line == "stop":
                    if loop_stack:
                        idx, count = loop_stack.pop()
                        if count > 1:
                            loop_stack.append((idx, count - 1))
                            i = idx + 1
                            continue

                # --- if / elif ---
                elif line.startswith("if ") or line.startswith("elif "):
                    prefix = "if " if line.startswith("if ") else "elif "
                    cond = line[len(prefix):].strip()
                    usermsg_val = local_vars.get("usermsg", "")
                    cond = cond.replace("{usermsg}", repr(usermsg_val))
                    try:
                        result = eval(cond, {"__builtins__": {}}, local_vars)
                    except Exception:
                        result = False
                    if not result:
                        curr_indent = indent
                        i += 1
                        while i < len(block) and block[i][0] > curr_indent:
                            i += 1
                        continue

                elif line.startswith("else"):
                    i += 1
                    continue

                # --- runtime set ---
                elif line.startswith("set "):
                    try:
                        key, val = line[4:].split("=", 1)
                        key = key.strip()
                        val = val.strip()
                        try:
                            val = val.format(**local_vars)
                        except Exception:
                            pass
                        local_vars[key] = val
                        self.variables[key] = val
                    except Exception:
                        pass

                # --- call function ---
                elif line.startswith("call "):
                    fname = line[5:].strip()
                    if fname in self.functions:
                        await self.run_block(self.functions[fname], update, context)

                # --- button definition line (skip silently) ---
                elif line.startswith("button ="):
                    pass

            except Exception as e:
                await update.message.reply_text(f"⚠️ Runtime error: {e}")

            i += 1

    # ------------------ MESSAGE HANDLER ------------------

    async def handle_usermsg(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        uid = update.effective_user.id
        if uid in self.asking:
            self.variables["usermsg"] = update.message.text
            del self.asking[uid]
        for block in self.usermsg_blocks:
            await self.run_block(block, update, context)

    # ------------------ TOKEN LOADER ------------------

    def load_token(self):
        """Load token from config.txt or .env if not already set in script."""
        if self.token:
            return
        for cfg in ["config.txt", ".env"]:
            if not os.path.exists(cfg):
                continue
            try:
                with open(cfg) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("TOKEN="):
                            self.token = line.split("=", 1)[1].strip().strip('"')
                            return
            except Exception:
                pass

    # ------------------ BOT RUNNER ------------------

    async def run(self):
        """Start the Telegram bot. Call after parse()."""
        self.load_token()

        if not self.token:
            raise RuntimeError(
                "Bot token not found.\n"
                '  • Add  bot "YOUR_TOKEN"  to your .wetg file\n'
                "  • OR create config.txt with  TOKEN=YOUR_TOKEN"
            )

        app = ApplicationBuilder().token(self.token).build()

        for cmd, block in self.commands.items():
            async def handler(
                update: Update,
                context: ContextTypes.DEFAULT_TYPE,
                block=block,
            ):
                await self.run_block(block, update, context)

            app.add_handler(CommandHandler(cmd.lstrip("/"), handler))
            print(f"✅ Registered /{cmd.lstrip('/')}")

        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_usermsg)
        )

        print("🚀 WETG Bot is running... Press Ctrl+C to stop.")

        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            print("\n🛑 Shutting down...")
            await app.updater.stop()
            await app.stop()
            await app.shutdown()