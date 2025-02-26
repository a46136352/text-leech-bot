import requests
import os
import schedule
import time
from telegram import Bot

# Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = "http://rozgarapinew.teachx.in/api"
bot = Bot(token=BOT_TOKEN)

def extract_and_upload():
    print("Starting extraction...")

    # 1. Get available batches
    batch_url = f"{API_URL}/batches"
    response = requests.get(batch_url)
    
    if response.status_code != 200:
        print("Failed to fetch batches!")
        return
    
    batches = response.json().get("data", [])
    
    for batch in batches:
        batch_id = batch.get("id")
        batch_name = batch.get("name")

        print(f"Processing Batch: {batch_name} (ID: {batch_id})")

        # 2. Get topics for the batch
        topics_url = f"{API_URL}/topics?batch_id={batch_id}"
        response = requests.get(topics_url)
        
        if response.status_code != 200:
            print(f"Failed to fetch topics for batch {batch_id}")
            continue
        
        topics = response.json().get("data", [])

        for topic in topics:
            topic_id = topic.get("id")
            topic_name = topic.get("name")

            print(f"Fetching Topic: {topic_name} (ID: {topic_id})")

            # 3. Get files for the topic
            files_url = f"{API_URL}/files?topic_id={topic_id}"
            response = requests.get(files_url)
            
            if response.status_code != 200:
                print(f"Failed to fetch files for topic {topic_id}")
                continue
            
            files = response.json().get("data", [])

            for file in files:
                file_url = file.get("download_url")
                file_name = file.get("name")

                print(f"Downloading: {file_name}")

                # 4. Download the file
                file_response = requests.get(file_url)
                if file_response.status_code != 200:
                    print(f"Failed to download {file_name}")
                    continue

                file_path = f"/tmp/{file_name}"
                with open(file_path, "wb") as f:
                    f.write(file_response.content)

                # 5. Upload to Telegram
                print(f"Uploading {file_name} to Telegram...")
                with open(file_path, "rb") as f:
                    bot.send_document(chat_id=CHAT_ID, document=f, caption=f"📄 {file_name} - {topic_name}")

                os.remove(file_path)  # Clean up after upload

    print("Upload process completed!")

# Schedule the job to run daily at 9 PM
schedule.every().day.at("21:00").do(extract_and_upload)

print("Bot is running. Waiting for schedule...")

while True:
    schedule.run_pending()
    time.sleep(60)  # Wait a minute before checking again
