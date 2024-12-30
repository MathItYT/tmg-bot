import base64
import discord


async def get_images_from_message(message: discord.Message) -> list[str]:
    result = []
    for attachment in message.attachments:
        content_type = attachment.content_type
        if content_type.startswith("image/"):
            b64 = base64.b64encode(await attachment.read()).decode("utf-8")
            result.append(f"data:{content_type};base64,{b64}")
    if message.reference:
        reply_message = await message.channel.fetch_message(message.reference.message_id)
        result.extend(await get_images_from_message(reply_message))
    return result