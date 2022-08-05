"""Functions and Info specific to the Telegram Bot
"""

import re

import requests as r


class T_info:
    license = re.sub(
        r"\b\n",
        " ",
        r.get(
            "https://gitlab.com/simple-stock-bots/simple-telegram-stock-bot/-/raw/master/LICENSE"
        ).text,
    )

    help_text = """

The bot detects _"Symbols"_ using either one `$` or two `$$` dollar signs before the symbol. One dollar sign is for a stock market ticker, while two is for a cryptocurrency coin. `/chart $$eth` would return a chart of the past month of data for Ethereum, while `/dividend $psec` returns dividend information for Prospect Capital stock.

Simply calling a symbol in any message that the bot can see will also return the price. So a message like: `I wonder if $$btc will go to the Moon now that $tsla accepts it as payment` would return the current price for both Bitcoin and Tesla. 

**Commands**
        - `/dividend $[symbol]` Dividend information for the symbol. 📅
        - `/intra $[symbol]` Plot of the stocks movement since the last market open.  📈
        - `/chart $[symbol]` Plot of the stocks movement for the past 1 month. 📊
        - `/news $[symbol]` News about the symbol. 📰
        - `/info $[symbol]` General information about the symbol. ℹ️
        - `/stat $[symbol]` Key statistics about the symbol. 🔢
        - `/cap $[symbol]` Market Capitalization of symbol. 💰
        - `/trending` Trending Stocks and Cryptos. 💬
        - `/help` Get some help using the bot. 🆘

**Inline Features**
    You can type @SimpleStockBot `[search]` in any chat or direct message to search for the stock bots full list of stock and crypto symbols and return the price. Then once you select the ticker want the bot will send a message as you in that chat with the latest stock price. Prices may be delayed by up to an hour.
    
    Market data is provided by [IEX Cloud](https://iexcloud.io)

    If you believe the bot is not behaving properly run `/status` or [get in touch](https://docs.simplestockbot.com/contact).
    """

commands = """
help - Get some help using the bot. 🆘
info - $[symbol] General information about the symbol. ℹ️
news - $[symbol] News about the symbol. 📰
stat - $[symbol] Key statistics about the symbol. 🔢
cap - $[symbol] Market Capitalization of symbol. 💰
dividend - $[symbol] Dividend info 📅
trending - Trending Stocks and Cryptos. 💬
intra - $[symbol] Plot since the last market open. 📈
chart - $[chart] Plot of the past month. 📊
"""  # Not used by the bot but for updaing commands with BotFather
