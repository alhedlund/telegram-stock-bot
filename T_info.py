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
        - `/info [symbol]` General information about the symbol. ℹ️
        - `/trending` Trending Cryptos. 💬
        - `/help` Get some help using the bot. 🆘

**Inline Features**
    You can type @SimpleStockBot `[search]` in any chat or direct message to search for the stock bots full list of stock and crypto symbols and return the price. Then once you select the ticker want the bot will send a message as you in that chat with the latest stock price. Prices may be delayed by up to an hour.
    
    Market data is provided by [IEX Cloud](https://iexcloud.io)

    If you believe the bot is not behaving properly run `/status` or [get in touch](https://docs.simplestockbot.com/contact).
    """

commands = """
help - Get some help using the bot. 🆘
info - [symbol] General information about the symbol. ℹ️
trending - Trending Cryptos. 💬
p - [symbol] Key statistics about the symbol. 🔢
c - [chart] [frequency] Plot of the past month. 📈
"""  # Not used by the bot but for updaing commands with BotFather
