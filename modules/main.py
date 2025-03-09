# Install necessary libraries
!pip install pyrogram tgcrypto

# Import required modules
import os
import requests
import asyncio
import threading
from pyrogram import Client, filters

# Configuration (replace with your own values)
API_ID = "28328736"
API_HASH = "802254a44896baa87f3083b7af36b2e5"
BOT_TOKEN = "6755775439:AAGkahjp3xK71u-jG6V0uQUR-xJgqLPt9yw"
ACCOUNT_ID = "6206459123001"
BCOV_POLICY = "BCpkADawqM1474MvKwYlMRZNBPoqkJY-UWm7zE1U769d5r5kqTjG0v8L-THXuVZtdIQJpfMPB37L_VJQxTKeNeLO2Eac_yMywEgyV9GjFDQ2LTiT4FEiHhKAUvdbx9ku6fGnQKSMB8J5uIDd"
bc_url = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos/"
bc_hdr = {"BCOV-POLICY": BCOV_POLICY}

# Initialize Pyrogram client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Download function
async def careerdl(app, message, headers, raw_text2, class_id, notes_id, prog, name):
    name = name.replace("/", "_")
    try:
        # Split class IDs
        num_id = class_id.split('&')
        output_text = ""

        for id_text in num_id:
            details_url = f"https://elearn.crwilladmin.com/api/v5/batch-detail/{raw_text2}?topicId={id_text}"
            response = requests.get(details_url, headers=headers)
            data = response.json()

            classes = data.get("data", {}).get("class_list", {}).get("classes", [])
            classes.reverse()

            for lesson in classes:
                try:
                    vid_id = str(lesson['id'])
                    lesson_name = lesson['lessonName']
                    lessonExt = lesson['lessonExt']
                    lessonUrl = requests.get(f"https://elearn.crwilladmin.com/api/v5/class-detail/{vid_id}", headers=headers).json().get('data', {}).get('class_detail', {}).get('lessonUrl', '')

                    if lessonExt == 'brightcove':
                        token_url = "https://elearn.crwilladmin.com/api/v5/livestreamToken"
                        params = {"base": "web", "module": "batch", "type": "brightcove", "vid": vid_id}
                        stoken = requests.get(token_url, headers=headers, params=params).json().get("data", {}).get("token", '')

                        link = f"{bc_url}{lessonUrl}/master.m3u8?bcov_auth={stoken}"
                        output_text += f"{lesson_name}: {link}\n"
                    elif lessonExt == 'youtube':
                        link = f"https://www.youtube.com/embed/{lessonUrl}"
                        output_text += f"{lesson_name}: {link}\n"

                except Exception as e:
                    print(f"Error processing lesson: {e}")

        # Save to file
        with open(f"{name}.txt", 'a') as f:
            f.write(output_text)

        # Process notes
        n_id = notes_id.split('&')
        for id in n_id:
            details_url = f"https://elearn.crwilladmin.com/api/v5/batch-notes/{raw_text2}?topicId={id}"
            notes_data = requests.get(details_url, headers=headers).json().get('data', {}).get('notesDetails', [])

            for note in notes_data:
                title = note['docTitle']
                url = note['docUrl'].replace("\\/", "/")
                with open(f"{name}.txt", 'a') as f:
                    f.write(f"{title}: {url}\n")

        # Send document
        await app.send_document(message.chat.id, document=f"{name}.txt", caption=f"Batch Name: `{name}`")

        # Clean up
        os.remove(f"{name}.txt")

    except Exception as e:
        await message.reply_text(str(e))
    finally:
        await prog.delete()

# Main handler
@app.on_message(filters.command("cw") & filters.user(SUDO_USERS))
async def career_will(app, message):
    try:
        input1 = await app.ask(message.chat.id, text="**Send ID & Password in format ID*Password or Send Token:**")
        raw_text = input1.text
        login_url = "https://elearn.crwilladmin.com/api/v5/login-other"

        if "*" in raw_text:
            email, password = raw_text.split("*")
            headers = {
                "Host": "elearn.crwilladmin.com",
                "Apptype": "web",
                "accept": "application/json",
                "content-type": "application/json; charset=utf-8",
                "accept-encoding": "gzip",
                "user-agent": "okhttp/3.9.1"
            }
            data = {"deviceType": "web", "password": password, "deviceModel": "chrome", "deviceVersion": "Chrome+122", "email": email}
            response = requests.post(login_url, headers=headers, json=data)
            token = response.json()["data"]["token"]
            await message.reply_text(f"**Login Successful**\n\n`{token}`")
        else:
            token = raw_text

        headers = {
            "Host": "elearn.crwilladmin.com",
            "Apptype": "web",
            "usertype": "2",
            "token": token,
            "accept-encoding": "gzip",
            "user-agent": "okhttp/3.9.1"
        }

        # Get batches
        batch_url = "https://elearn.crwilladmin.com/api/v5/my-batch"
        topicid = requests.get(batch_url, headers=headers).json()["data"]["batchData"]

        FFF = "**BATCH-ID - BATCH NAME**\n\n"
        for data in topicid:
            FFF += f"`{data['id']}` - **{data['batchName']}**\n\n"

        await message.reply_text(f"**Here are your batches:**\n\n{FFF}")
        input2 = await app.ask(message.chat.id, text="**Now send the Batch ID to download**")
        raw_text2 = input2.text

        # Get class IDs and notes
        class_url = f"https://elearn.crwilladmin.com/api/v5/batch-topic/{raw_text2}?type=class"
        class_data = requests.get(class_url, headers=headers).json()['data']['batch_topic']
        class_id = "&".join([str(data['id']) for data in class_data])

        notes_url = f"https://elearn.crwilladmin.com/api/v5/batch-topic/{raw_text2}?type=notes"
        notes_data = requests.get(notes_url, headers=headers).json()['data']['batch_topic']
        notes_id = "&".join([str(data['id']) for data in notes_data])

        prog = await message.reply_text("**Extracting videos links... Please wait**")

        # Start download in a separate thread
        threading.Thread(target=lambda: asyncio.run(careerdl(app, message, headers, raw_text2, class_id, notes_id, prog, name))).start()

    except Exception as e:
        await message.reply_text(str(e))

# Start the bot
app.run()
