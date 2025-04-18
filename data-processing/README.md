If you want to pipe params to another module (e.g., a job‑search function), simply call it instead of send:

from jobs_module import find_jobs        # your own module

@client.event
async def on_message(msg):
    ...
    params = router.route(msg.content)
    results = find_jobs(**params)
    await msg.channel.send(results)
