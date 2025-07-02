from telegram import Update, BotCommand
from telegram.constants import ChatAction, ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
from src.rss_parser import load_json_url
from src.preprocessing import convert_news_to_documents, clean_documents
from src.clustering import cluster_documents
from src.digest_generator import generate_summary_for_cluster, generate_detailed_response
import logging
import os
import re
from dotenv import load_dotenv
import httpx

load_dotenv()

TELEGRAM_TOKEN = os.environ["BOT_TOKEN"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def set_commands(application):
    commands = [
        BotCommand(command="start", description="Start work with Bot"),
        BotCommand(command="digest", description="Get the news digest"),
        BotCommand(command="detail", description="Get detailed summary of a cluster")
    ]
    await application.bot.set_my_commands(commands)

#Function for command in bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text(
        f"Hi {update.effective_user.first_name}!\n\n"
        "I'm your News Digest Bot.\n\n"
        "Use /digest to get today's digest.\n"
        "Use /detail <cluster_number> to get detailed summary of a cluster."
    )

#Function Escapes special characters for Telegram MarkdownV2.
# Guarantees that the input is a string.
def escape_markdown(text) -> str:
    if text is None:
        text = ""
    elif not isinstance(text, str):
        text = str(text)
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

#Sends long texts in parts so as not to exceed Telegram's limit.
async def send_long_message(update: Update, text: str, chunk_size: int = 4000):
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN_V2)


async def digest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        # Check if there are any news items already loaded in user_data
        all_news = context.user_data.get('all_news')
        news_index = context.user_data.get('news_index', 0)

        if not all_news:
            # First launch - loading all news
            await update.message.reply_text("Loading and processing news...")

            url = "https://newsapi.org/v2/everything?q=science&apiKey=cae4948f170f49b69c797bb9dc8ab14b"
            news = load_json_url(url)

            if not news:
                await update.message.reply_text("No news found.")
                return

            documents = convert_news_to_documents(news)
            cleaned_documents = clean_documents(documents)

            if not cleaned_documents:
                await update.message.reply_text("Unable to clear documents.")
                return

            context.user_data['all_news'] = cleaned_documents
            context.user_data['news_index'] = 0
            all_news = cleaned_documents
            news_index = 0

        # Check at the end of the list
        if news_index >= len(all_news):
            await update.message.reply_text(
                "You have viewed all the news!\n"
                "Use /start to start over."
            )
            return

        # Let's take the current news
        current_doc = all_news[news_index]

        # Increase the index for the next call
        context.user_data['news_index'] = news_index + 1

        context.user_data['clusters'] = {0: [current_doc]}

        # Generate summary
        summary = generate_summary_for_cluster([current_doc])
        if not summary:
            summary = "Unable to generate a summary digest."

        # We receive a link
        url_value = current_doc.metadata.get('url')
        if not isinstance(url_value, str):
            url_value = str(url_value)

        # Forming the text
        text = (
            f"*News {news_index + 1} form {len(all_news)}*\n\n"
            f"*Title:* {escape_markdown(current_doc.metadata.get('title', 'No title'))}\n\n"
            f"{escape_markdown(summary)}\n\n"
            f"[Read all]({escape_markdown(url_value)})"
        )

        await send_long_message(update, text)

        await update.message.reply_text(
            "For a more detailed analysis of this news item, use /detail 1."
        )

    except Exception as e:
        logger.error("Error in digest", exc_info=True)
        await update.message.reply_text("An error occurred while processing the news item..")



async def detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args:
            await update.message.reply_text(
                "Please enter a keyword for your search.\n\n"
                "For example:\n/detail quantum"
            )
            return

        query = " ".join(args)

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        await update.message.reply_text(f"Searching for news by request: {query}...")

        # Add a timeout to the request
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey=cae4948f170f49b69c797bb9dc8ab14b"
        try:
            news = load_json_url(url, timeout=30)
        except httpx.ReadTimeout:
            await update.message.reply_text("The timeout for a response from the news service has been exceeded. Please try again later.")
            return

        if not news:
            await update.message.reply_text(f"No news found for the query ‘{query}’.")
            return

        documents = convert_news_to_documents(news)
        cleaned_documents = clean_documents(documents)

        if not cleaned_documents:
            await update.message.reply_text("Unable to process news.")
            return

        matched_docs = [
            doc for doc in cleaned_documents
            if query.lower() in doc.metadata.get('title', '').lower()
            or query.lower() in doc.page_content.lower()
        ]

        if not matched_docs:
            await update.message.reply_text(f"No relevant news found for your query.'{query}'.")
            return

        detailed_summary = generate_detailed_response(matched_docs)
        if not detailed_summary:
            detailed_summary = "Unable to generate a detailed digest."

        first_url = matched_docs[0].metadata.get('url')
        if first_url:
            detailed_summary += f"\n\n[Read the article]({first_url})"

        escaped_text = escape_markdown(detailed_summary)
        await send_long_message(update, escaped_text)

    except Exception as e:
        logger.error("Error in detail", exc_info=True)
        await update.message.reply_text("An error occurred while generating the detailed digest.")


async def on_startup(app):
    await set_commands(app)


def run_bot():
    app = Application.builder().token(TELEGRAM_TOKEN).pool_timeout(30).post_init(on_startup).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("digest", digest))
    app.add_handler(CommandHandler("detail", detail))

    logger.info("Bot started. Listening for commands.")
    app.run_polling()
