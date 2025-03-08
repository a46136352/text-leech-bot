from pytube import YouTube
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import os

# Apna Telegram bot ka token yahan daalo
TOKEN = '6755775439:AAGkahjp3xK71u-jG6V0uQUR-xJgqLPt9yw'

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Mujhe YouTube ka link bhejo, main tumhare liye video download karunga.")

def download_video(update: Update, context: CallbackContext):
    url = update.message.text
    update.message.reply_text("Video download ho raha hai... Thoda intezaar karo.")

    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()
        file_path = stream.download()

        update.message.reply_text("Download complete! Video bhej raha hoon...")

        with open(file_path, 'rb') as video:
            update.message.reply_video(video)

        os.remove(file_path)

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
