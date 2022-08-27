import pandas as pd
import logging


class Symbol:
    """
    symbol: What the user calls it. ie tsla or btc
    id: What the api expects. ie tsla or bitcoin
    name: Human readable. ie Tesla or Bitcoin
    tag: Uppercase tag to call the symbol. ie $TSLA or $$BTC
    """

    def __init__(self, symbol) -> None:
        self.symbol = symbol

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} instance of {self.symbol} at {id(self)}>"

    def __str__(self) -> str:
        return self.symbol


class Coin(Symbol):
    """Cryptocurrency Object. Gets data from CoinGecko."""

    def __init__(self, symbol: pd.DataFrame) -> None:
        if len(symbol) > 1:
            logging.info(f"Crypto with shared id:\n\t{symbol.baseCurrency}")
            symbol = symbol.head(1)

        self.symbol = symbol.baseCurrency.values[0]


# ToDo: implement NFT subclass and add floor price commands
# class NFT(Symbol):
#     def __init__(self, symbol: pd.DataFrame) -> None:
#         pass
