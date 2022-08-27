# Works with Python 3.8
import datetime
import html
import io
import json
import logging
import os
import random
import string
import traceback
from logging import critical, debug, error, info, warning
from uuid import uuid4

import mplfinance as mpf
import telegram
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    LabeledPrice,
    Update,
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    Updater,
)

from symbol_router import Router
from T_info import T_info

TELEGRAM_TOKEN = os.environ["TELEGRAM"]

s = Router()
t = T_info()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
info("Bot script started.")


def start(update: Update, context: CallbackContext):
    """Send help text when the command /start is issued."""
    info(f"Start command ran by {update.message.chat.username}")
    update.message.reply_text(
        text=t.help_text,
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_notification=True,
    )


def help(update: Update, context: CallbackContext):
    """Send help text when the command /help is issued."""
    info(f"Help command ran by {update.message.chat.username}")
    update.message.reply_text(
        text=t.help_text,
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_notification=True,
    )


def license(update: Update, context: CallbackContext):
    """Send bots license when the /license command is issued."""
    info(f"License command ran by {update.message.chat.username}")
    update.message.reply_text(
        text=t.license,
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_notification=True,
    )


def status(update: Update, context: CallbackContext):
    """Gather status of bot and dependant services and return important status updates."""
    warning(f"Status command ran by {update.message.chat.username}")
    bot_resp_time = (
        datetime.datetime.now(update.message.date.tzinfo) - update.message.date
    )

    bot_status = s.status(
        f"It took {bot_resp_time.total_seconds()} seconds for the bot to get your message."
    )

    update.message.reply_text(
        text=bot_status,
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def chart(update: Update, context: CallbackContext):
    """returns a chart of the past month of data for a symbol"""
    info(f"Chart command ran by {update.message.chat.username}")

    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip().split("@")[0] == "/c":
        update.message.reply_text(
            "This command returns a chart of the stocks movement for the past month.\nExample: /c btc"
        )
        return

    symbols = s.find_symbols(message)
    frequency = s.find_chart_interval(message)

    if len(symbols):
        symbol = symbols[0]
    else:
        update.message.reply_text("No symbols or coins found.")
        return

    df = s.chart_reply(symbol, frequency)

    if df.empty:
        update.message.reply_text(
            text="Invalid symbol please see `/help` for usage details.",
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_notification=True,
        )
        return

    context.bot.send_chat_action(
        chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO
    )

    buf = io.BytesIO()
    mpf.plot(
        df,
        type="candle",
        title=f"\n{symbol.symbol}",
        volume="volume" in df.keys(),
        style="mike",
        savefig=dict(fname=buf, dpi=400, bbox_inches="tight"),
    )
    buf.seek(0)

    update.message.reply_photo(
        photo=buf,
        caption=f"\n {frequency} chart for {symbol.symbol} from {df.first_valid_index().strftime('%d, %b %Y')}"
        + f" to {df.last_valid_index().strftime('%d, %b %Y')}\n\n{s.stat_reply([symbol])[0]}",
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_notification=True,
    )


def price(update: Update, context: CallbackContext):
    """returns key statistics on symbol"""
    info(f"Price command ran by {update.message.chat.username}")
    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip().split("@")[0] == "/p":
        update.message.reply_text(
            "This command returns key statistics for a symbol.\nExample: /p btc"
        )
        return

    symbols = s.find_symbols(message)

    if symbols:
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        for reply in s.stat_reply(symbols):
            update.message.reply_text(
                text=reply,
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_notification=True,
            )


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    warning('Update "%s" caused error "%s"', update, error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    err_code = "".join([random.choice(string.ascii_lowercase) for i in range(5)])
    warning(f"Logging error: {err_code}")

    if update:
        message = (
            f"An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )
        warning(message)
    else:
        warning(tb_string)


def main():
    """Start the context.bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("license", license))
    dp.add_handler(CommandHandler("p", price))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("status", status))

    # Charting can be slow so they run async.
    dp.add_handler(CommandHandler("c", chart, run_async=True))
    dp.add_handler(CommandHandler("chart", chart, run_async=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
