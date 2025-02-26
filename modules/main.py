import requests
import json
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import requests
import json
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
import os

logging.basicConfig(level=logging.INFO)

# Set API credentials
API_ID = int(os.getenv("API_ID", "28328736"))  # Replace 123456 with your actual API_ID
API_HASH = os.getenv("API_HASH", "802254a44896baa87f3083b7af36b2e5")  # Replace with your actual API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN", "6755775439:AAGkahjp3xK71u-jG6V0uQUR-xJgqLPt9yw")  # Replace with your bot token

# Initialize Pyrogram Client
bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)
# Initialize Pyrogram Client
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Bot Setup
@bot.on_message(filters.command(["txt"]))
async def account_login(bot: Client, m: Message):
    await m.reply_text(
        "**Choose Your Institute:**\n"
        "**1. Ankit With Rojgar:** `rozgarapinew.teachx.in`\n"
        "**2. The Last Exam:** `lastexamapi.teachx.in`\n"
        "**3. The Mission Institute:** `missionapi.appx.co.in`"
    )

    input01: Message = await bot.listen(m.chat.id)
    institute = input01.text.strip()

    if institute not in ["rozgarapinew.teachx.in", "lastexamapi.teachx.in", "missionapi.appx.co.in"]:
        await m.reply_text("Invalid Institute. Please enter a valid one.")
        return

    await m.reply_text("Send **ID & Password** in this format: `ID*Password`")
    input1: Message = await bot.listen(m.chat.id)

    try:
        user_id, password = input1.text.split("*")
    except ValueError:
        await m.reply_text("Invalid format! Use `ID*Password`")
        return

    # Login request
    login_url = f"https://{institute}/post/login"
    headers = {
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-ID": "-2",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    credentials = {"email": user_id, "password": password}

    response = requests.post(login_url, data=credentials, headers=headers)
    if response.status_code != 200:
        await m.reply_text("Login failed. Check your credentials.")
        return

    output = response.json()
    user_id = output["data"]["userid"]
    token = output["data"]["token"]

    await m.reply_text("✅ **Login Successful!**")

    # Headers for subsequent requests
    api_headers = {
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-ID": user_id,
        "Authorization": token,
        "User-Agent": "okhttp/4.9.1"
    }

    # Fetching user batches
    batch_url = f"https://{institute}/get/mycourse?userid={user_id}"
    res1 = requests.get(batch_url, headers=api_headers)
    
    try:
        batch_data = res1.json()["data"]
    except (KeyError, json.JSONDecodeError):
        await m.reply_text("Error fetching batches.")
        return

    batch_list = "**Your Available Batches:**\n\n"
    for batch in batch_data:
        batch_list += f"📚 `{batch['id']}` - **{batch['course_name']}**\n"

    await m.reply_text(batch_list)
    
    # Get batch ID from user
    await m.reply_text("Send the **Batch ID** to proceed:")
    input2: Message = await bot.listen(m.chat.id)
    batch_id = input2.text.strip()

    # Fetch Subjects
    subject_url = f"https://{institute}/get/allsubjectfrmlivecourseclass?courseid={batch_id}"
    res2 = requests.get(subject_url, headers=api_headers)
    
    try:
        subjects = res2.json()["data"]
    except (KeyError, json.JSONDecodeError):
        await m.reply_text("Error fetching subjects.")
        return

    await m.reply_text(str(subjects))

    await m.reply_text("Enter the **Subject ID** from the above response:")
    input3: Message = await bot.listen(m.chat.id)
    subject_id = input3.text.strip()

    # Fetch Topics
    topic_url = f"https://{institute}/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={subject_id}"
    res3 = requests.get(topic_url, headers=api_headers)

    try:
        topics = res3.json()["data"]
    except (KeyError, json.JSONDecodeError):
        await m.reply_text("Error fetching topics.")
        return

    topic_list = "**Available Topics:**\n\n"
    topic_ids = []
    for topic in topics:
        topic_list += f"📝 `{topic['topicid']}` - **{topic['topic_name']}**\n"
        topic_ids.append(topic['topicid'])

    await m.reply_text(topic_list)

    # Get topic IDs from user
    await m.reply_text(
        "Send the **Topic IDs** separated by `&` to download (e.g., `1&2&3`):"
    )
    input4: Message = await bot.listen(m.chat.id)
    selected_topics = input4.text.strip().split("&")

    # Get Resolution from user
    await m.reply_text("Now send the **Resolution**:")
    input5: Message = await bot.listen(m.chat.id)
    resolution = input5.text.strip()

    # Fetch Video Links
    final_data = []
    for topic_id in selected_topics:
        topic_url = f"https://{institute}/get/livecourseclassbycoursesubtopconceptapiv3?topicid={topic_id}&start=-1&courseid={batch_id}&subjectid={subject_id}"
        res4 = requests.get(topic_url, headers=api_headers)

        try:
            topic_data = res4.json()["data"]
        except (KeyError, json.JSONDecodeError):
            await m.reply_text(f"Error fetching data for Topic ID {topic_id}.")
            continue

        for data in topic_data:
            title = data["Title"].replace(" : ", " ").strip()
            encrypted_url = data.get("download_link") or data.get("pdf_link")

            # Decrypt URL
            key = "638udh3829162018".encode("utf8")
            iv = "fedcba9876543210".encode("utf8")
            ciphertext = bytearray.fromhex(b64decode(encrypted_url.encode()).hex())
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_url = unpad(cipher.decrypt(ciphertext), AES.block_size).decode("utf-8")

            final_data.append(f"{title}: {decrypted_url}")

    # Save and send file
    file_name = f"DownloadLinks_{batch_id}.txt"
    with open(file_name, "w") as f:
        f.write("\n".join(final_data))

    await m.reply_document(file_name)
    await m.reply_text("✅ **Download Links Generated Successfully!**")

bot.run()
if __name__ == "__main__":
    asyncio.run(main())
