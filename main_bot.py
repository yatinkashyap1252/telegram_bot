# import yt_dlp
# import asyncio
# import os
# import base64
# import subprocess
# from dotenv import load_dotenv
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# load_dotenv()

# TOKEN = os.getenv("TOKEN")
# yt_username = os.getenv("YT_USERNAME")
# yt_password = os.getenv("YT_PASSWORD")
# COOKIES_PATH = os.getenv("YT_COOKIES", "youtube_cookies.txt")

# print(f"Using bot token: {TOKEN}")

# # Decode and create cookies file if stored in an environment variable
# cookies_base64 = os.getenv("YT_COOKIES_BASE64")
# if cookies_base64:
#     with open(COOKIES_PATH, "w") as f:
#         f.write(base64.b64decode(cookies_base64).decode())
# elif not os.path.exists(COOKIES_PATH):
#     print(f"Warning: {COOKIES_PATH} does not exist. YouTube downloads may not work.")

# def extract_download_url(url, format_type):
#     options = {
#         'quiet': True,
#         'format': 'bestaudio' if format_type == 'audio' else 'best',
#         'noplaylist': True,
#         'extract_flat': True,
#         'cookies': COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,  # Use cookies only if available
#     }
#     try:
#         with yt_dlp.YoutubeDL(options) as ydl:
#             info = ydl.extract_info(url, download=False)
#             return info.get('url')
#     except Exception as e:
#         print(f"Error extracting URL: {e}")
#         return None

# async def start(update: Update, context):
#     await update.message.reply_text("👋 Welcome! Send me a video link (YouTube, Instagram, etc.), and I'll fetch it for you!")

# async def help_command(update: Update, context):
#     await update.message.reply_text("ℹ️ Send a video link, and I'll ask whether you want the Audio or Video version.")

# async def process_link(update: Update, context):
#     url = update.message.text
#     keyboard = [[InlineKeyboardButton("🎵 Audio", callback_data=f"audio|{url}"),
#                  InlineKeyboardButton("📹 Video", callback_data=f"video|{url}")]]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text("Do you want Audio or Video?", reply_markup=reply_markup)

# async def button_handler(update: Update, context):
#     query = update.callback_query
#     await query.answer()
#     format_type, url = query.data.split('|')
#     await query.edit_message_text("⏳ Processing your request... Please wait!")

#     try:
#         download_url = extract_download_url(url, format_type)
#         if not download_url:
#             await query.edit_message_text("❌ Failed to fetch the media. Please try another link.")
#             return
        
#         await query.message.reply_text(f"✅ Here is your {format_type}: [Click here]({download_url})", parse_mode="Markdown")
#     except Exception as e:
#         await query.message.reply_text(f"⚠️ Error: {str(e)}")

# async def main():
#     app = Application.builder().token(TOKEN).build()
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(CommandHandler("help", help_command))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_link))
#     app.add_handler(CallbackQueryHandler(button_handler))
    
#     print("🚀 Bot is running...")
#     await app.run_polling()

# if __name__ == "__main__":
#     import nest_asyncio
#     nest_asyncio.apply()
#     asyncio.run(main())

import yt_dlp
import asyncio
import os
import base64
import subprocess
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
yt_username = os.getenv("YT_USERNAME")
yt_password = os.getenv("YT_PASSWORD")
COOKIES_PATH = os.getenv("YT_COOKIES", "youtube_cookies.txt")

print(f"Using bot token: {TOKEN[:6]}******")  # Hide full token for security

# Decode and save cookies file if provided in base64 format
cookies_base64 = os.getenv("YT_COOKIES_BASE64")
if cookies_base64:
    try:
        with open(COOKIES_PATH, "w") as f:
            f.write(base64.b64decode(cookies_base64).decode())
        print("✅ Cookies file created successfully!")
    except Exception as e:
        print(f"❌ Error decoding cookies: {e}")
elif not os.path.exists(COOKIES_PATH):
    print(f"⚠️ Warning: {COOKIES_PATH} does not exist. YouTube downloads may not work.")

def extract_download_url(url, format_type):
    options = {
        'quiet': True,
        'format': 'bestaudio' if format_type == 'audio' else 'best',
        'noplaylist': True,
        'extract_flat': False,
        'cookies': COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,
    }
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'url' in info:
                return info['url']
            elif 'entries' in info and len(info['entries']) > 0:
                return info['entries'][0]['url']
            else:
                return None
    except Exception as e:
        print(f"Error extracting URL: {e}")
        return None

async def start(update: Update, context):
    await update.message.reply_text("👋 Welcome! Send me a video link (YouTube, Instagram, etc.), and I'll fetch it for you!")

async def help_command(update: Update, context):
    await update.message.reply_text("ℹ️ Send a video link, and I'll ask whether you want the Audio or Video version.")

async def process_link(update: Update, context):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("⚠️ Please send a valid video link.")
        return

    keyboard = [[InlineKeyboardButton("🎵 Audio", callback_data=f"audio|{url}"),
                 InlineKeyboardButton("📹 Video", callback_data=f"video|{url}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Do you want Audio or Video?", reply_markup=reply_markup)

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    format_type, url = query.data.split('|', 1)
    await query.edit_message_text("⏳ Processing your request... Please wait!")

    try:
        download_url = extract_download_url(url, format_type)
        if not download_url:
            await query.edit_message_text("❌ Failed to fetch the media. Please try another link.")
            return
        await query.message.reply_text(f"✅ Here is your {format_type}: [Click here]({download_url})", parse_mode="Markdown")
    except Exception as e:
        await query.message.reply_text(f"⚠️ Error: {str(e)}")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_link))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🚀 Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
