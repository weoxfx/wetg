"""
WETG CLI — invoked via:
    python -m wetg run mybot.wetg
    python -m wetg new mybot.wetg
    python -m wetg check mybot.wetg
    wetg run mybot.wetg   (after pip install)
"""

import sys
import os
import asyncio
from . import __version__, __author__
from .interpreter import Wetg

VERSION_HEADER = "Super Weox"

TEMPLATE = '''\
# ─────────────────────────────────────────
# {filename} — created by WETG v{version}
# Replace YOUR_TOKEN with your bot token
# from @BotFather on Telegram
# ─────────────────────────────────────────

bot "YOUR_TOKEN_HERE"

set welcome=Welcome!

on /start
    send "👋 Hi {{user.name}}! {{welcome}}"
    send "Type /help to see commands."

on /help
    send "/start — greet\\n/ping — pong!\\n/echo — repeat your message"

on /ping
    send "🏓 Pong!"

on /echo
    ask "What should I echo back?"

on usermsg
    send "You said: {{usermsg}}"
'''

CYAN   = "\033[0;36m"
GREEN  = "\033[0;32m"
YELLOW = "\033[1;33m"
RED    = "\033[0;31m"
BOLD   = "\033[1m"
NC     = "\033[0m"

def logo():
    print(f"{CYAN}{BOLD}")
    print("  ██╗    ██╗███████╗████████╗ ██████╗ ")
    print("  ██║    ██║██╔════╝╚══██╔══╝██╔════╝ ")
    print("  ██║ █╗ ██║█████╗     ██║   ██║  ███╗")
    print("  ██║███╗██║██╔══╝     ██║   ██║   ██║")
    print("  ╚███╔███╔╝███████╗   ██║   ╚██████╔╝")
    print("   ╚══╝╚══╝ ╚══════╝   ╚═╝    ╚═════╝ ")
    print(f"{NC}{YELLOW}  v{__version__} {VERSION_HEADER} — One-File Telegram Bot Engine{NC}")
    print()

def help_text():
    logo()
    print(f"{BOLD}Usage:{NC}")
    print("  wetg run <file.wetg>     Run a WETG bot")
    print("  wetg new <file.wetg>     Create a bot from template")
    print("  wetg check <file.wetg>   Validate a .wetg file")
    print("  wetg version             Show version")
    print("  wetg help                Show this help")
    print()
    print(f"{BOLD}Examples:{NC}")
    print("  wetg new mybot.wetg")
    print("  wetg run mybot.wetg")
    print()

def cmd_run(filepath):
    if not filepath:
        print(f"{RED}❌ No file specified. Usage: wetg run mybot.wetg{NC}")
        sys.exit(1)
    if not os.path.exists(filepath):
        print(f"{RED}❌ File not found: {filepath}{NC}")
        sys.exit(1)

    print(f"{GREEN}🔥 WETG v{__version__} {VERSION_HEADER}{NC}")

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    bot = Wetg(code)
    bot.parse()

    try:
        asyncio.run(bot.run())
    except RuntimeError as e:
        print(f"{RED}❌ {e}{NC}")
        sys.exit(1)

def cmd_new(filepath):
    if not filepath:
        print(f"{RED}❌ Specify a filename. Usage: wetg new mybot.wetg{NC}")
        sys.exit(1)
    if os.path.exists(filepath):
        print(f"{YELLOW}⚠️  File already exists: {filepath}{NC}")
        sys.exit(1)

    content = TEMPLATE.format(
        filename=os.path.basename(filepath),
        version=__version__,
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"{GREEN}✅ Created: {filepath}{NC}")
    print(f"   Edit it and add your bot token, then:")
    print(f"   {CYAN}wetg run {filepath}{NC}")

def cmd_check(filepath):
    if not filepath:
        print(f"{RED}❌ No file specified.{NC}")
        sys.exit(1)
    if not os.path.exists(filepath):
        print(f"{RED}❌ File not found: {filepath}{NC}")
        sys.exit(1)

    print(f"{CYAN}🔍 Checking {filepath} ...{NC}")

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    bot = Wetg(code)
    bot.parse()

    token_ok = bool(bot.token)
    print(f"  Token defined  : {'✅ Yes' if token_ok else '❌ No — add: bot \"TOKEN\"'}")
    print(f"  Commands       : {len(bot.commands)} → {', '.join('/' + c.lstrip('/') for c in bot.commands) if bot.commands else 'none'}")
    print(f"  usermsg blocks : {len(bot.usermsg_blocks)}")
    print(f"  Functions      : {len(bot.functions)} → {', '.join(bot.functions) if bot.functions else 'none'}")
    print(f"  Variables      : {len(bot.variables)} → {', '.join(bot.variables) if bot.variables else 'none'}")
    print(f"  Imports        : {', '.join(bot.imports) if bot.imports else 'none'}")

    if not token_ok:
        print(f"\n{YELLOW}⚠️  Add your bot token before running!{NC}")
    else:
        print(f"\n{GREEN}✅ Looks good! Run with: wetg run {filepath}{NC}")

def main():
    args = sys.argv[1:]

    if not args:
        help_text()
        return

    cmd = args[0]
    arg2 = args[1] if len(args) > 1 else None

    if cmd == "run":
        cmd_run(arg2)
    elif cmd == "new":
        cmd_new(arg2)
    elif cmd == "check":
        cmd_check(arg2)
    elif cmd in ("version", "--version", "-v"):
        print(f"WETG v{__version__} {VERSION_HEADER}")
    elif cmd in ("help", "--help", "-h"):
        help_text()
    elif cmd.endswith(".wetg"):
        # shortcut: wetg mybot.wetg
        cmd_run(cmd)
    else:
        print(f"{RED}❌ Unknown command: {cmd}{NC}")
        print("Run 'wetg help' for usage.")
        sys.exit(1)

if __name__ == "__main__":
    main()