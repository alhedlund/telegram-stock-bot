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


def symbol_detect_image(update: Update, context: CallbackContext):
    """
    Makes image captions into text then passes the `update` and `context`
        to symbol detect so that it can reply cashtags in image captions.
    """
    if update.message.caption:
        update.message.text = update.message.caption
        symbol_detect(update, context)


def symbol_detect(update: Update, context: CallbackContext):
    """
    Runs on any message that doesn't have a command and searches for cashtags,
        then returns the prices of any symbols found.
    """
    try:
        message = update.message.text
        chat_id = update.message.chat_id
        if "$" in message:
            symbols = s.find_symbols(message)
            info("Looking for Symbols")
        else:
            return
    except AttributeError as ex:
        info(ex)
        return
    if symbols:
        # Let user know bot is working
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        info(f"Symbols found: {symbols}")

        for reply in s.price_reply(symbols):
            update.message.reply_text(
                text=reply,
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_notification=True,
            )


def dividend(update: Update, context: CallbackContext):
    """/dividend or /div command and then finds dividend info on that symbol."""
    info(f"Dividend command ran by {update.message.chat.username}")
    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip().split("@")[0] == "/dividend":
        update.message.reply_text(
            "This command gives info on the next dividend date for a symbol.\nExample: /dividend $tsla"
        )
        return

    symbols = s.find_symbols(message)

    if symbols:
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        for reply in s.dividend_reply(symbols):
            update.message.reply_text(
                text=reply,
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_notification=True,
            )


def news(update: Update, context: CallbackContext):
    """/news command then finds news info on that symbol."""
    info(f"News command ran by {update.message.chat.username}")
    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip().split("@")[0] == "/news":
        update.message.reply_text(
            "This command gives the most recent english news for a symbol.\nExample: /news $tsla"
        )
        return

    symbols = s.find_symbols(message, trending_weight=10)

    if symbols:
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        for reply in s.news_reply(symbols):
            update.message.reply_text(
                text=reply,
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_notification=True,
            )


def information(update: Update, context: CallbackContext):
    """/info command then finds info on that symbol."""
    info(f"Information command ran by {update.message.chat.username}")
    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip().split("@")[0] == "/info":
        update.message.reply_text(
            "This command gives information on a symbol.\nExample: /info $tsla"
        )
        return

    symbols = s.find_symbols(message)

    if symbols:
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        for reply in s.info_reply(symbols):
            update.message.reply_text(
                text=reply,
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_notification=True,
            )


def search(update: Update, context: CallbackContext):
    """
    Searches on full list of stocks and crypto descriptions
    then returns the top matches in order of smallest symbol name length.
    """
    info(f"Search command ran by {update.message.chat.username}")
    message = update.message.text.replace("/search ", "")
    chat_id = update.message.chat_id

    if message.strip().split("@")[0] == "/search":
        update.message.reply_text(
            "This command searches for symbols supported by the bot.\nExample: /search Tesla Motors or /search $tsla"
        )
        return

    context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    queries = s.inline_search(message, matches=10)
    if not queries.empty:
        reply = "*Search Results:*\n`$ticker` : Company Name\n`" + ("-" * 21) + "`\n"
        for _, query in queries.iterrows():
            desc = query["description"]
            reply += "`" + desc.replace(": ", "` : ") + "\n"

        update.message.reply_text(
            text=reply,
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_notification=True,
        )


def intra(update: Update, context: CallbackContext):
    """returns a chart of intraday data for a symbol"""
    info(f"Intra command ran by {update.message.chat.username}")

    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip().split("@")[0] == "/intra":
        update.message.reply_text(
            "This command returns a chart of the stocks movement since the most recent market open.\nExample: /intra $tsla"
        )
        return

    symbols = s.find_symbols(message, trending_weight=5)
    symbol = symbols[0]

    if len(symbols):
        symbol = symbols[0]
    else:
        update.message.reply_text("No symbols or coins found.")
        return

    df = s.intra_reply(symbol)
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
        title=f"\n{symbol.name}",
        volume="volume" in df.keys(),
        style="mike",
        savefig=dict(fname=buf, dpi=400, bbox_inches="tight"),
    )
    buf.seek(0)

    update.message.reply_photo(
        photo=buf,
        caption=f"\nIntraday chart for {symbol.name} from {df.first_valid_index().strftime('%d %b at %H:%M')} to"
        + f" {df.last_valid_index().strftime('%d %b at %H:%M')}"
        + f"\n\n{s.price_reply([symbol])[0]}",
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_notification=True,
    )


def chart(update: Update, context: CallbackContext):
    """returns a chart of the past month of data for a symbol"""
    info(f"Chart command ran by {update.message.chat.username}")

    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip().split("@")[0] == "/chart":
        update.message.reply_text(
            "This command returns a chart of the stocks movement for the past month.\nExample: /chart $tsla"
        )
        return

    symbols = s.find_symbols(message, trending_weight=10)

    if len(symbols):
        symbol = symbols[0]
    else:
        update.message.reply_text("No symbols or coins found.")
        return

    df = s.chart_reply(symbol)
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
        title=f"\n{symbol.name}",
        volume="volume" in df.keys(),
        style="yahoo",
        savefig=dict(fname=buf, dpi=400, bbox_inches="tight"),
    )
    buf.seek(0)

    update.message.reply_photo(
        photo=buf,
        caption=f"\n1 Month chart for {symbol.name} from {df.first_valid_index().strftime('%d, %b %Y')}"
        + f" to {df.last_valid_index().strftime('%d, %b %Y')}\n\n{s.price_reply([symbol])[0]}",
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_notification=True,
    )


def stat(update: Update, context: CallbackContext):
    """returns key statistics on symbol"""
    info(f"Stat command ran by {update.message.chat.username}")
    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip().split("@")[0] == "/stat":
        update.message.reply_text(
            "This command returns key statistics for a symbol.\nExample: /stat $tsla"
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


def cap(update: Update, context: CallbackContext):
    """returns market cap for symbol"""
    info(f"Cap command ran by {update.message.chat.username}")
    message = update.message.text
    chat_id = update.message.chat_id

    if message.strip().split("@")[0] == "/cap":
        update.message.reply_text(
            "This command returns the market cap for a symbol.\nExample: /cap $tsla"
        )
        return

    symbols = s.find_symbols(message)

    if symbols:
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

        for reply in s.cap_reply(symbols):
            update.message.reply_text(
                text=reply,
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_notification=True,
            )


def trending(update: Update, context: CallbackContext):
    """returns currently trending symbols and how much they've moved in the past trading day."""
    info(f"Trending command ran by {update.message.chat.username}")

    chat_id = update.message.chat_id

    context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)

    trending_list = s.trending()
    info(trending_list)

    update.message.reply_text(
        text=trending_list,
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_notification=True,
    )


def inline_query(update: Update, context: CallbackContext):
    """
    Handles inline query. Searches by looking if query is contained
        in the symbol and returns matches in alphabetical order.
    """
    # info(f"Inline command ran by {update.message.chat.username}")
    info(f"Query: {update.inline_query.query}")

    ignored_queries = {"$", "$$", " ", ""}

    if update.inline_query.query.strip() in ignored_queries:
        default_message = """
        You can type:\n@SimpleStockBot `[search]`\nin any chat or direct message to search for the stock bots full list of stock and crypto symbols and return the price.
        """

        update.inline_query.answer(
            [
                InlineQueryResultArticle(
                    str(uuid4()),
                    title="Please enter a query. It can be a ticker or a name of a company.",
                    input_message_content=InputTextMessageContent(
                        default_message, parse_mode=telegram.ParseMode.MARKDOWN
                    ),
                )
            ]
        )

    matches = s.inline_search(update.inline_query.query)

    results = []
    for _, row in matches.iterrows():

        results.append(
            InlineQueryResultArticle(
                str(uuid4()),
                title=row["description"],
                input_message_content=InputTextMessageContent(
                    row["price_reply"], parse_mode=telegram.ParseMode.MARKDOWN
                ),
            )
        )

        if len(results) == 5:
            update.inline_query.answer(results, cache_time=60 * 60)
            info("Inline Command was successful")
            return
    update.inline_query.answer(results)


def rand_pick(update: Update, context: CallbackContext):
    """For the gamblers. Returns a random symbol to buy and a sell date"""
    info(
        f"Someone is gambling! Random_pick command ran by {update.message.chat.username}"
    )

    update.message.reply_text(
        text=s.random_pick(),
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

    # update.message.reply_text(
    #     text=f"An error has occured. Please inform @MisterBiggs if the error persists. Error Code: `{err_code}`",
    #     parse_mode=telegram.ParseMode.MARKDOWN,
    # )

    # Finally, send the message
    # update.message.reply_text(text=message, parse_mode=telegram.ParseMode.HTML)
    # update.message.reply_text(text="Please inform the bot admin of this issue.")


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
    dp.add_handler(CommandHandler("dividend", dividend))
    dp.add_handler(CommandHandler("div", dividend))
    dp.add_handler(CommandHandler("news", news))
    dp.add_handler(CommandHandler("info", information))
    dp.add_handler(CommandHandler("stat", stat))
    dp.add_handler(CommandHandler("stats", stat))
    dp.add_handler(CommandHandler("cap", cap))
    dp.add_handler(CommandHandler("trending", trending))
    dp.add_handler(CommandHandler("search", search))
    dp.add_handler(CommandHandler("random", rand_pick))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("inline", inline_query))

    # Charting can be slow so they run async.
    dp.add_handler(CommandHandler("intra", intra, run_async=True))
    dp.add_handler(CommandHandler("intraday", intra, run_async=True))
    dp.add_handler(CommandHandler("day", intra, run_async=True))
    dp.add_handler(CommandHandler("chart", chart, run_async=True))
    dp.add_handler(CommandHandler("month", chart, run_async=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, symbol_detect))
    dp.add_handler(MessageHandler(Filters.photo, symbol_detect_image))

    # Inline Bot commands
    dp.add_handler(InlineQueryHandler(inline_query))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
