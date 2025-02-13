import yt_dlp
import asyncio
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

load_dotenv()

TOKEN=os.getenv("TOKEN")
COOKIES_PATH = os.getenv("YT_COOKIES", "youtube_cookies.txt")

def extract_download_url(url, format_type):
    options = {
        'quiet': True,
        'format': 'bestaudio' if format_type == 'audio' else 'best',
        'noplaylist': True,
        'extract_flat': True,
        'cookies': 'youtube_cookies.txt',
    }
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('url')
    except Exception as e:
        print(f"Error extracting URL: {e}")
        return None

async def start(update: Update, context):
    await update.message.reply_text("Welcome! Send me a video link (YouTube, Instagram, etc.), and I'll fetch it for you!")

async def help_command(update: Update, context):
    await update.message.reply_text("Send a video link, and I'll ask whether you want the Audio or Video version.")

async def process_link(update: Update, context):
    url = update.message.text
    keyboard = [[InlineKeyboardButton("Audio", callback_data=f"audio|{url}"),
                 InlineKeyboardButton("Video", callback_data=f"video|{url}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Do you want Audio or Video?", reply_markup=reply_markup)

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    format_type, url = query.data.split('|')
    await query.edit_message_text("Processing your request... Please wait!")

    try:
        # Extract the correct media URL
        download_url = extract_download_url(url, format_type)
        if not download_url:
            await query.edit_message_text("Failed to fetch the media. Please try another link.")
            return
        
        # Provide the direct working URL
        await query.message.reply_text(f"Here is your {format_type}: [Click here]({download_url})", parse_mode="Markdown")
    except Exception as e:
        await query.message.reply_text(f"Error: {str(e)}")


async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_link))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())