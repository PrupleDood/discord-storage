
from bot.db_files import db 

from discord import File, TextChannel, Guild
import os
import io

async def upload_file(file_path: str, channel: TextChannel):
    size_in_bytes = 25 * 1024 * 1024 # 25Mb

    discord_files = []

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(size_in_bytes)

            stream = io.BytesIO(chunk)

            if not chunk:
                break
            
            discord_files.append(File(stream))

    for i, file in enumerate(discord_files):
        message = await channel.send(file = file)

        filename = os.path.split(file_path)[1]

        db.add_file(db.File(
            parent_file = filename,
            file_index = i,
            message_data = message
        ))


async def download_file(parent_file: str, guild: Guild):
    entries = db.get_file_entries(parent_file)

    sorted_entries = sorted(entries, key = lambda entry : entry["file_index"])
    message_ids = [entry["message_id"] for entry in sorted_entries]

    channel = await guild.fetch_channel(sorted_entries[0]["channel_id"])

    dwn_path = os.path.join(os.getcwd(), f"downloads/{parent_file}")

    messages = [await channel.fetch_message(msg_id) for msg_id in message_ids]
    attachments = [await message.attachments[0].read() for message in messages] # Returns bytes

    with open(dwn_path, "wb") as file:
        for attachment in attachments:
            file.write(attachment)