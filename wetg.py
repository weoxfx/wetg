"""
WETG v7 "Super Weox" - One File Telegram Bot Interpreter
Usage:
    wetg run mybot.wetg
    OR: python wetg.py mybot.wetg
"""

import sys, asyncio, random, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

VERSION = "7"
VERSION_HEADER = "Super Weox"

# ------------------ USER & BOT INFO ------------------
class User:
    def __init__(self, tg_user):
        self.id = tg_user.id
        self.name = tg_user.first_name
        self.username = tg_user.username or ""

class BotInfo:
    def __init__(self, bot):
        self.id = bot.id
        self.username = bot.username
        self.name = bot.first_name

# ------------------ WETG INTERPRETER ------------------
class Wetg:
    def __init__(self, code):
        self.code = code.splitlines()
        self.token = None
        self.commands = {}
        self.usermsg_blocks = []
        self.variables = {}
        self.asking = {}
        self.ask_callbacks = {}
        self.functions = {}
        self.imports = {}

    def parse(self):
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

            if stripped.startswith("wetg "): continue
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
                    print(f"⚠️  Invalid set statement: {stripped}")
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

    # ------------------ RUN BLOCK ------------------
    async def run_block(self, block, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = User(update.effective_user)
        botinfo = BotInfo(context.bot)
        local_vars = self.variables.copy()
        local_vars.update({
            "user": user,
            "bot": botinfo,
            "msg": update.message,
            "usermsg": update.message.text if update.message else "",
            "random": random,
            **self.imports
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

                # --- send with ---
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
                        btn_raw = local_vars.get("button", None)
                        if btn_raw:
                            try:
                                btn_label, btn_url = str(btn_raw).strip("[]").replace('"', '').replace("'", '').split(",", 1)
                                keyboard = InlineKeyboardMarkup([[
                                    InlineKeyboardButton(btn_label.strip(), url=btn_url.strip())
                                ]])
                            except Exception:
                                pass
                        else:
                            for j in range(i - 1, -1, -1):
                                bline = block[j][1]
                                if bline.startswith("button =") or bline.startswith("set button ="):
                                    btn_part = bline.split("=", 1)[1].strip()
                                    try:
                                        btn_label, btn_url = btn_part.strip("[]").replace('"', '').split(",", 1)
                                        keyboard = InlineKeyboardMarkup([[
                                            InlineKeyboardButton(btn_label.strip(), url=btn_url.strip())
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
                        if "times" in parts:
                            times = int(parts[0])
                        else:
                            times = int(local_vars.get(parts[0], 0))
                    except Exception:
                        times = 0
                    loop_stack.append((i, times))
                    i += 1
                    continue

                # --- stop (end of loop body) ---
                elif line == "stop":
                    if loop_stack:
                        idx, count = loop_stack.pop()
                        if count > 1:
                            loop_stack.append((idx, count - 1))
                            i = idx + 1
                            continue

                # --- if / elif / else ---
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

                # --- set (runtime) ---
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

                # --- button = (definition line, skip silently) ---
                elif line.startswith("button ="):
                    pass

            except Exception as e:
                await update.message.reply_text(f"⚠️ Runtime error: {e}")

            i += 1

    # ------------------ HANDLE USER MSG ------------------
    async def handle_usermsg(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if uid in self.asking:
            self.variables["usermsg"] = update.message.text
            del self.asking[uid]
            # run any on usermsg blocks so the answer can be processed
        for block in self.usermsg_blocks:
            await self.run_block(block, update, context)

    # ------------------ RUN BOT ------------------
    async def run(self):
        # Try to load token from config.txt if not found in script
        if not self.token:
            for cfg in ["config.txt", ".env"]:
                try:
                    with open(cfg) as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("TOKEN="):
                                self.token = line.split("=", 1)[1].strip().strip('"')
                except Exception:
                    pass

        if not self.token:
            print("❌ Bot token not found.")
            print("   Add:  bot \"YOUR_TOKEN\"  to your .wetg file")
            print("   OR create config.txt with:  TOKEN=YOUR_TOKEN")
            return

        app = ApplicationBuilder().token(self.token).build()

        for cmd, block in self.commands.items():
            async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE, block=block):
                await self.run_block(block, update, context)
            app.add_handler(CommandHandler(cmd.replace("/", ""), handler))
            print(f"✅ Registered /{cmd.lstrip('/')}")

        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_usermsg))

        print("🚀 WETG Bot is running... Press Ctrl+C to stop.")

        # Fix: use low-level async API instead of run_polling()
        # to avoid event loop conflicts (especially on Termux/Python 3.12)
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        try:
            await asyncio.Event().wait()  # block forever
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            print("\n🛑 Shutting down...")
            await app.updater.stop()
            await app.stop()
            await app.shutdown()


# ------------------ MAIN ------------------
def main():
    args = sys.argv[1:]

    # Support: wetg run file.wetg  OR  wetg file.wetg  OR  python wetg.py file.wetg
    if not args:
        print(f"🔥 WETG v{VERSION} {VERSION_HEADER}")
        print("Usage:")
        print("  wetg run mybot.wetg")
        print("  python wetg.py mybot.wetg")
        return

    # Strip 'run' subcommand if present
    if args[0] == "run":
        args = args[1:]

    if not args:
        print("❌ No .wetg file specified.")
        return

    filepath = args[0]

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    wetg = Wetg(code)
    wetg.parse()
    asyncio.run(wetg.run())


if __name__ == "__main__":
    print(f"🔥 WETG v{VERSION} {VERSION_HEADER}")
    main()
