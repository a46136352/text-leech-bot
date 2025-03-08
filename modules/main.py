import os
import yt_dlp
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = '6755775439:AAGkahjp3xK71u-jG6V0uQUR-xJgqLPt9yw'

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Mujhe YouTube ka link bhejo, main tumhare liye video download karunga.")

def download_video(update: Update, context: CallbackContext):
    url = update.message.text
    update.message.reply_text("Video download ho raha hai... Thoda intezaar karo.")

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloaded_video.mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open('downloaded_video.mp4', 'rb') as video:
            update.message.reply_video(video)

        os.remove('downloaded_video.mp4')
        update.message.reply_text("Video bhej diya gaya hai!")

    except Exception as e:
        update.message.reply_text(f"Kuch gadbad hui: {e}")

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_video))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
