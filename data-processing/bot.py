# bot.py  (only on_message handler changed)
import json, discord, os
from t5_router import T5CommandRouter
# ... (intents + client setup stays the same)

router = T5CommandRouter()

@client.event
async def on_message(msg: discord.Message):
    if msg.author.bot:
        return
    if msg.content.startswith("!"):
        return

    params = router.route(msg.content)           # <- now a dict
    # Here you could forward `params` to another module instead of printing.
    await msg.channel.send(f"Parameters → ```json\n{json.dumps(params, indent=2)}```")
