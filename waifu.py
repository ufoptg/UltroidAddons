# Ultroid - UserBot
# Copyright (C) 2023-2024 @TeamUltroid
#
# This file is a part of < https://github.com/ufoptg/UltroidBackup/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/ufoptg/UltroidBackup/blob/main/LICENSE/>.
# By @TrueSaiyan
"""
❍ Commands Available -

• `{i}waifu` or {i}waifu <type>
    Send sfw waifu or select.

• `{i}waifu2` or {i}waifu2 <type>
    Send a nsfw waifu.

~ NSFW: `waifu` `neko` `trap` `blowjob`

~ SFW: `waifu` `neko` `shinobu` `megumin`
     `bully` `cuddle` `cry` `hug` `awoo`
     `kiss` `lick` `pat` `smug` `bonk`
     `blush` `smile` `wave` `highfive`
     `nom` `bite` `glomp` `slap` `kill`
     `kick` `happy` `wink` `poke` `dance`
     `cringe` `handhold` `yeet`
"""

import asyncio
import random

import requests
from telethon.errors.rpcerrorlist import MessageIdInvalidError

from . import ultroid_bot, ultroid_cmd

class WaifuApiUrl:
    def __init__(
        self,
        url: str = "api.waifu.pics",
        method: str = None,
        parameter: str = None,
        allow_web: str = "https",
    ):
        self.url = url
        self.method = method
        self.parameter = parameter
        self.allow_web = allow_web

    def checking(self):
        api_url = f"{self.allow_web}://{self.url}/{self.method}/{self.parameter}"
        return api_url

@ultroid_cmd(
    pattern=r"waifu(|2)(?:\s|$)([\s\S]*)",
)
async def _(event):
    raw_text = event.raw_text.split(" ", 1)
    try:
        load = await event.eor("Getting Data")
    except MessageIdInvalidError:
        pass
    cat = None

    # Create an instance of the PrivateApiUrl class
    private_api = WaifuApiUrl()

    # Set the method and parameter based on the command
    if event.pattern_match.group(1) == "2":
        private_api.method = "nsfw"
        if len(raw_text) < 2:
            cat = ["waifu", "neko", "trap", "blowjob"]
        else:
            cat = raw_text[1].split()
    elif cat is None:
        private_api.method = "sfw"
        if len(raw_text) < 2:
            cat = [
                "waifu",
                "neko",
                "shinobu",
                "megumin",
                "bully",
                "cuddle",
                "cry",
                "hug",
                "awoo",
                "kiss",
                "lick",
                "pat",
                "smug",
                "bonk",
                "yeet",
                "blush",
                "smile",
                "wave",
                "highfive",
                "handhold",
                "nom",
                "bite",
                "glomp",
                "slap",
                "kill",
                "kick",
                "happy",
                "wink",
                "poke",
                "dance",
                "cringe",
            ]
        else:
            cat = raw_text[1].split()

    cat_phrase = random.choice(cat)
    private_api.parameter = cat_phrase
    api_url = private_api.checking()

    response = requests.get(api_url)

    image_url = response.json()["url"]

    await asyncio.sleep(1)
    await load.delete()
    await event.client.send_file(
        event.chat_id, image_url, reply_to=event.reply_to_msg_id
    )
