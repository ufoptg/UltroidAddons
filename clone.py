# Ported From DarkCobra , Originally By Uniborg
# Ultroid ~ UserBot
#
# This file is a part of < https://github.com/ufoptg/UltroidBackup/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/ufoptg/UltroidBackup/blob/main/LICENSE/>.

"""
❍ Commands Available

• `{i}clone <reply/username>`
    clone the identity of user.

• `{i}revert`
    Revert to your original identity
"""

import html
import os

from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.errors.rpcerrorlist import AboutTooLongError
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName

from . import *


@ultroid_cmd(pattern="clone ?(.*)", fullsudo=True)
async def clone_identity(event):
    eve = await event.eor("Processing...")
    reply_message = await event.get_reply_message()
    whoiam = await event.client(GetFullUserRequest(ultroid_bot.uid))

    original_bio_key = f"{str(ultroid_bot.me.id)}_bio"
    original_fname_key = f"{ultroid_bot.uid}_first_name"
    original_lname_key = f"{ultroid_bot.uid}_last_name"

    if whoiam.full_user.about:
        udB.set_key(original_bio_key, whoiam.full_user.about)
    udB.set_key(original_fname_key, whoiam.users[0].first_name)
    if whoiam.users[0].last_name:
        udB.set_key(original_lname_key, whoiam.users[0].last_name)

    replied_user, error_msg = await get_full_user(event)
    if replied_user is None:
        await eve.edit(str(error_msg))
        return

    user_id = replied_user.users[0].id
    profile_pic = await event.client.download_profile_photo(user_id)
    first_name = html.escape(replied_user.users[0].first_name or "")
    last_name = html.escape(replied_user.users[0].last_name or "⁪⁬⁮⁮⁮")
    user_bio = replied_user.full_user.about or ""

    if len(user_bio) > 70:
        user_bio = user_bio[:67] + "..."

    try:
        await event.client(UpdateProfileRequest(first_name=first_name, last_name=last_name, about=user_bio))
    except AboutTooLongError:
        await eve.edit("Failed to update bio, even after shortening.")
        return

    if profile_pic:
        pfile = await event.client.upload_file(profile_pic)
        await event.client(UploadProfilePhotoRequest(file=pfile))
        os.remove(profile_pic)

    cloned_photo = await event.client.get_profile_photos("me", limit=1)
    if cloned_photo:
        udB.set_key(f"{ultroid_bot.uid}_cloned_photo", cloned_photo[0])

    await eve.delete()
    await event.client.send_message(
        event.chat_id, f"I am {first_name} from now...", reply_to=reply_message
    )


@ultroid_cmd(pattern="revert$")
async def revert_identity(event):
    bio_key = f"{str(ultroid_bot.me.id)}_bio"
    fname_key = f"{ultroid_bot.uid}_first_name"
    lname_key = f"{ultroid_bot.uid}_last_name"
    photo_key = f"{ultroid_bot.uid}_cloned_photo"

    bio = udB.get_key(bio_key) if udB.get_key(bio_key) is not None else "No original bio saved."
    first_name = udB.get_key(fname_key) if udB.get_key(fname_key) is not None else OWNER_NAME
    last_name = udB.get_key(lname_key) if udB.get_key(lname_key) is not None else ""

    
    cloned_photo = udB.get_key(photo_key)
    if cloned_photo:
        await event.client(DeletePhotosRequest(id=[cloned_photo]))

    await event.client(UpdateProfileRequest(first_name=first_name, last_name=last_name, about=bio))
    await event.eor("Successfully reverted to your original account!")

    
    udB.del_key(bio_key)
    udB.del_key(fname_key)
    udB.del_key(lname_key)
    udB.del_key(photo_key)


async def get_full_user(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_id = previous_message.forward.sender_id or previous_message.forward.channel_id if previous_message.forward else previous_message.sender_id
        replied_user = await event.client(GetFullUserRequest(user_id))
        return replied_user, None
    else:
        input_str = event.pattern_match.group(1) or ""
        try:
            mention_entity = event.message.entities[0]
            if isinstance(mention_entity, MessageEntityMentionName):
                replied_user = await event.client(GetFullUserRequest(mention_entity.user_id))
                return replied_user, None
            user_object = await event.client.get_entity(input_str)
            replied_user = await event.client(GetFullUserRequest(user_object.id))
            return replied_user, None
        except Exception as e:
            return None, e
