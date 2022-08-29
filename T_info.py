"""
Functions and Info specific to the Telegram Bot
"""

import re

import requests as r


class T_info:
    license = re.sub(
        r"\b\n",
        " ",
        r.get(
            "https://github.com/alhedlund/telegram-stock-bot/-/raw/master/LICENSE"
        ).text,
    )

    help_text = """

**Commands**
        - `/p [symbol]` Key statistics about the symbol.  🔢
        - `/c [symbol] [frequency]` Plot of the stocks movement for specified period. 📈
        - `/help` Get some help using the bot. 🆘
    """

commands = """
help - Get some help using the bot. 🆘
info - [symbol] General information about the symbol. ℹ️
p - [symbol] Key statistics about the symbol. 🔢
c - [chart] [frequency] Plot of the past month. 📈
"""  # Not used by the bot but for updaing commands with BotFather
