import discord

from google import genai
from google.genai import types, errors


async def get_files_from_message(client: genai.Client, message: discord.Message) -> list[types.Part]:
    result = []
    for attachment in message.attachments:
        try:
            if attachment.size >= 20971520:
                continue
            part = types.Part.from_bytes(await attachment.read(), attachment.content_type)
            result.append(part)
        except discord.HTTPException:
            pass
        except errors.ClientError:
            pass
    if message.reference:
        ref_message = await message.channel.fetch_message(message.reference.message_id)
        result.extend(await get_files_from_message(client, ref_message))
    return result