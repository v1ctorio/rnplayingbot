token = 'TELEGRAM_TOKEN'
sptoken = 'SPOTIFY_TOKEN'
authorized = False
import logging
from uuid import uuid4

import tekore as tk

from telegram import InlineQueryResultArticle, InlineQueryResultAudio, InputTextMessageContent, InlineKeyboardMarkup,Update, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hi!")


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""

    if not authorized:
        await update.inline_query.answer(
            [
                InlineQueryResultArticle(
                    id=uuid4(),
                    title="Authorize",
                    input_message_content=InputTextMessageContent(
                        f"Please authorize me by clicking [here](tg://resolve?domain={context.bot.username}&start=auth)",
                        parse_mode=ParseMode.MARKDOWN,
                    ),

                )
            ]
        )
        return

    spotify = tk.Spotify(sptoken)
    results = spotify.playback_currently_playing(tracks_only=True,)
    print(results)
    if results is None:
        await update.inline_query.answer(
            [
                InlineQueryResultArticle(
                    id=uuid4(),
                    title="No song playing",
                    input_message_content=InputTextMessageContent(
                        "No song playing"
                    ),
                )
            ]
        )
        return
    # reply with the current song
    await update.inline_query.answer(
        [
            InlineQueryResultAudio(

                id=uuid4(),
                title=results.item.name,
                performer=results.item.artists[0].name,
                audio_url=results.item.preview_url,
                reply_markup=InlineKeyboardMarkup.from_button(
                    InlineKeyboardButton(
                        "Open on Spotify",
                        url=results.item.external_urls["spotify"],
                    )
                ),
            )
        ]
    )

    return


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(InlineQueryHandler(inline_query))
    application.run_polling()


if __name__ == "__main__":
    main()
