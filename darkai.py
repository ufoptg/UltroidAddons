# Written by @TrueSaiyan
# Nimbus ~ UserBot
#
# This file is a part of < https://github.com/ufoptg/UltroidAddons/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/ufoptg/Nimbus/blob/main/LICENSE/>.
"""
**Get Answers from DarkAI(GPT-4o) a Uncensored Psychiatrist**

• `{i}darkai` Talk to a Psychiatrist
    ~ • `{i}darkai hello`
• `{i}darkai -c` Clear Chat History
"""

import json
import requests
from collections import deque
from . import ultroid_cmd, LOGS, run_async

darkai_chat_history_SIZE = 80

darkai_chat_history = deque(maxlen=darkai_chat_history_SIZE)

def format_prompt(messages):
    """Format messages for the DarkAI API."""
    return "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

async def fetch_chat_response(prompt, model):
    """Interact with DarkAI API and retrieve a response."""
    api_url = "https://darkai.foundation/chat"
    headers = {
        "accept": "text/event-stream",
        "content-type": "application/json",
        "origin": "https://www.aiuncensored.info",
        "referer": "https://www.aiuncensored.info/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    }
    data = {
        "query": prompt,
        "model": model,
    }

    response = requests.post(api_url, headers=headers, json=data, stream=True)
    if response.status_code == 200:
        final_message = None
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    json_data = decoded_line[6:]
                    if json_data:
                        try:
                            parsed_data = json.loads(json_data)
                            if parsed_data.get("event") == "final-response":
                                final_message = parsed_data.get("data", {}).get("message")
                        except json.JSONDecodeError:
                            LOGS.warning("Failed to decode JSON: %s", json_data)
        return final_message
    else:
        LOGS.warning("Error: %d - %s", response.status_code, response.text)
        return None

@ultroid_cmd(pattern="darkai (.+)")
async def darkai_chat(e):
    """Command to interact with the DarkAI API using the 'darkai' keyword with chat history."""
    user_input = e.pattern_match.group(1)
    if not user_input:
        return await e.eor("Provide a query to send to DᴀʀᴋAI.")

    if user_input == "-c":
        darkai_chat_history.clear()
        return await e.eor("Cleared DᴀʀᴋAI Chat History!", time=6)

    darkai_chat_history.append({"role": "user", "content": user_input})
    prompt = format_prompt(darkai_chat_history)
    
    moi = await e.eor("Cᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ DᴀʀᴋAI…")
    try:
        response = await fetch_chat_response(prompt, "gpt-4o")
        if response:
            darkai_chat_history.append({"role": "assistant", "content": response})
    except Exception as exc:
        LOGS.warning(exc, exc_info=True)
        return await moi.edit(f"Error occurred: {exc}")
    else:
        if response:
            await moi.edit(f"DᴀʀᴋAI:\n\n{response}")
        else:
            await moi.edit("Failed to get a response from DᴀʀᴋAI.")
