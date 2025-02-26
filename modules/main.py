import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import os

# Pehle environment variables set kar
os.environ["API_ID"] = "28328736"
os.environ["API_HASH"] = "802254a44896baa87f3083b7af36b2e5"
os.environ["BOT_TOKEN"] = "6755775439:AAGkahjp3xK71u-jG6V0uQUR-xJgqLPt9yw"

API_URL = "http://rozgarapinew.teachx.in/api"

# Ab inhe variables me assign kar
API_ID = int(os.getenv("API_ID"))  # API_ID ko int me convert karna zaroori hai
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
# Start Pyrogram Client
app = Client("bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_sessions = {}

@app.on_message(filters.command("rwa"))
async def rwa_command(client, message: Message):
    """Handles /rwa command and asks for ID & Password"""
    await message.reply_text("🔑 Send your ID and password in this manner: id*password OR send your Token:")

@app.on_message(filters.text & ~filters.command)
async def login(client, message: Message):
    """Handles login with ID & Password OR Token"""
    chat_id = message.chat.id
    credentials = message.text

    if "*" in credentials:
        user_id, password = credentials.split("*")
        login_url = f"{API_URL}/login"
        response = requests.post(login_url, json={"id": user_id, "password": password})
    else:
        token = credentials
        response = requests.get(f"{API_URL}/validate_token", headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        token = response.json().get("token")
        user_sessions[chat_id] = token
        await message.reply_text("✅ Login successful! Fetching Batches...")
        await send_batches(client, message)
    else:
        await message.reply_text("❌ Login failed! Try again using /rwa.")

async def send_batches(client, message: Message):
    """Fetches and sends available batch IDs"""
    chat_id = message.chat.id
    token = user_sessions.get(chat_id)

    batch_url = f"{API_URL}/batches"
    response = requests.get(batch_url, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await message.reply_text("⚠️ Failed to fetch batches!")
        return

    batches = response.json().get("data", [])
    batch_msg = "📚 Available Batches:\n" + "\n".join([f"🔹 {b['name']} (ID: {b['id']})" for b in batches])
    await message.reply_text(batch_msg + "\n\n📝 Send a Batch ID to continue:")

@app.on_message(filters.text & ~filters.command)
async def send_subjects(client, message: Message):
    """Fetches and sends available subject IDs"""
    chat_id = message.chat.id
    token = user_sessions.get(chat_id)

    batch_id = message.text
    subject_url = f"{API_URL}/subjects?batch_id={batch_id}"
    response = requests.get(subject_url, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await message.reply_text("⚠️ Failed to fetch subjects!")
        return

    subjects = response.json().get("data", [])
    subject_msg = "📖 Available Subjects:\n" + "\n".join([f"📌 {s['name']} (ID: {s['id']})" for s in subjects])
    await message.reply_text(subject_msg + "\n\n📝 Send a Subject ID to continue:")

@app.on_message(filters.text & ~filters.command)
async def send_topics(client, message: Message):
    """Fetches and sends available topic IDs"""
    chat_id = message.chat.id
    token = user_sessions.get(chat_id)

    subject_id = message.text
    topic_url = f"{API_URL}/topics?subject_id={subject_id}"
    response = requests.get(topic_url, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await message.reply_text("⚠️ Failed to fetch topics!")
        return

    topics = response.json().get("data", [])
    topic_msg = "📌 Available Topics:\n" + "\n".join([f"📍 {t['name']} (ID: {t['id']})" for t in topics])
    await message.reply_text(topic_msg + "\n\n📝 Send a Topic ID to extract .txt:")

@app.on_message(filters.text & ~filters.command)
async def extract_txt(client, message: Message):
    """Extracts data and sends .txt file"""
    chat_id = message.chat.id
    token = user_sessions.get(chat_id)

    topic_id = message.text
    file_url = f"{API_URL}/files?topic_id={topic_id}"
    response = requests.get(file_url, headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        await message.reply_text("⚠️ Failed to fetch files!")
        return

    files = response.json().get("data", [])

    # Create TXT content
    txt_content = f"📂 Extracted Files for Topic ID {topic_id}:\n\n"
    for file in files:
        file_name = file.get("name")
        file_type = file.get("type")
        file_url = file.get("download_url")
        txt_content += f"📄 {file_name} ({file_type})\n🔗 {file_url}\n\n"

    # Save and send TXT file
    txt_filename = f"/tmp/topic_{topic_id}.txt"
    with open(txt_filename, "w") as f:
        f.write(txt_content)

    await client.send_document(chat_id=chat_id, document=txt_filename, caption="📄 Extracted .txt file")
    os.remove(txt_filename)

# Run the bot
app.run()
