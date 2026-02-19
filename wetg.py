"""
WETG v7 "Super Weox" - One File Telegram Bot Interpreter
Usage:
1. Create your bot code file, e.g., mybot.wetg
2. Add your bot token in bot.wetg:
   bot "123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
   OR create config.txt with TOKEN=...
3. Run:
   python wetg.py mybot.wetg
"""

import sys, asyncio, random, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

VERSION_HEADER = "Super Weox"

# ------------------ USER & BOT INFO ------------------
class User:
    def __init__(self, tg_user):
        self.id = tg_user.id
        self.name = tg_user.first_name
        self.username = tg_user.username

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
                    try: self.imports[m] = __import__(m)
                    except: print(f"⚠️ Failed import {m}")
                continue
            if stripped.startswith("bot "):
                try: self.token = stripped.split('"')[1]
                except: pass
                continue
            if stripped.startswith("function "):
                if current_function:
                    self.functions[current_function] = function_block
                current_function = stripped[9:].strip()
                function_block = []
                continue
            if stripped.startswith("set "):
                try:
                    key,val = stripped[4:].split("=",1)
                    self.variables[key.strip()] = val.strip()
                except:
                    print(f"⚠️ Invalid set: {stripped}")
                continue
            if stripped.startswith("on "):
                if current_cmd:
                    if is_usermsg: self.usermsg_blocks.append(current_block)
                    else: self.commands[current_cmd] = current_block
                current_cmd = stripped[3:].strip()
                current_block = []
                is_usermsg = current_cmd=="usermsg"
                continue
            if current_function: function_block.append((indent,stripped))
            else: current_block.append((indent,stripped))

        if current_function: self.functions[current_function] = function_block
        if current_cmd:
            if is_usermsg: self.usermsg_blocks.append(current_block)
            else: self.commands[current_cmd] = current_block

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
            **self.imports
        })

        i = 0
        loop_stack = []
        while i < len(block):
            indent, line = block[i]

            try:
                if line.startswith("ask "):
                    q = line[4:].strip().strip('"')
                    await update.message.reply_text(q)
                    self.asking[update.effective_user.id]=True
                    return

                elif "with " in line:
                    parts = line.split("with")
                    text = parts[0].replace("send","").strip().strip('"')
                    send_type = parts[1].strip()
                    try: text = text.format(**local_vars)
                    except: text = text
                    if send_type=="button":
                        for j in range(i-1,-1,-1):
                            if block[j][1].startswith("button ="):
                                btn_part = block[j][1].split("=",1)[1].strip()
                                btn_label,btn_url=btn_part.strip("[]").replace('"','').split(",")
                                keyboard=InlineKeyboardMarkup([[InlineKeyboardButton(btn_label.strip(),url=btn_url.strip())]])
                                await update.message.reply_text(text, reply_markup=keyboard)
                                break
                    elif send_type=="image":
                        try: await update.message.reply_photo(InputFile(text))
                        except: await update.message.reply_text(f"⚠️ Cannot send image {text}")
                    i+=1; continue

                elif line.startswith("send "):
                    text=line[5:].strip().strip('"')
                    try: text=text.format(**local_vars)
                    except: text=text
                    await update.message.reply_text(text)

                elif line.startswith("loop "):
                    parts=line[5:].split()
                    if "times" in parts: times=int(parts[0])
                    else: times=int(local_vars.get(parts[0],0))
                    loop_stack.append((i,times))
                    i+=1; continue
                elif line=="stop":
                    if loop_stack:
                        idx,count=loop_stack.pop()
                        if count>1:
                            loop_stack.append((idx,count-1))
                            i=idx+1; continue

                elif line.startswith("if "):
                    cond=line[3:].strip().replace("{usermsg}",f'"{local_vars.get("usermsg","")}"')
                    if eval(cond): i+=1; continue
                    else: curr_indent=indent; i+=1
                    while i<len(block) and block[i][0]>curr_indent: i+=1; continue
                elif line.startswith("elif "):
                    cond=line[5:].strip().replace("{usermsg}",f'"{local_vars.get("usermsg","")}"')
                    if eval(cond): i+=1; continue
                    else: curr_indent=indent; i+=1
                    while i<len(block) and block[i][0]>curr_indent: i+=1; continue
                elif line.startswith("else"): i+=1; continue
                elif line.startswith("call "):
                    f=line[5:].strip()
                    if f in self.functions: await self.run_block(self.functions[f], update, context)

            except Exception as e:
                await update.message.reply_text(f"⚠️ Warning: {e}")

            i+=1

    # ------------------ HANDLE USER MSG ------------------
    async def handle_usermsg(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id in self.asking:
            self.variables["usermsg"]=update.message.text
            del self.asking[update.effective_user.id]
            return
        for block in self.usermsg_blocks:
            await self.run_block(block, update, context)

    # ------------------ RUN BOT ------------------
    async def run(self):
        if not self.token:
            try:
                with open("config.txt") as f:
                    for line in f:
                        if line.startswith("TOKEN="):
                            self.token=line.strip().split("=")[1]
            except:
                print("❌ Bot token not found. Add in .wetg or config.txt")
                return

        app=ApplicationBuilder().token(self.token).build()
        for cmd,block in self.commands.items():
            async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE, block=block):
                await self.run_block(block, update, context)
            app.add_handler(CommandHandler(cmd.replace("/",""),handler))
            print(f"✅ Registered {cmd}")
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,self.handle_usermsg))
        print("🚀 WETG Bot Running...")
        await app.run_polling()

# ------------------ MAIN ------------------
def main():
    if len(sys.argv)<2:
        print("Usage: python wetg.py mybot.wetg")
        return

    with open(sys.argv[1],"r",encoding="utf-8") as f:
        code=f.read()

    wetg = Wetg(code)
    wetg.parse()
    asyncio.run(wetg.run())

if __name__=="__main__":
    print(f"🔥 WETG v7 {VERSION_HEADER}")
    main()
