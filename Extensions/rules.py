from interactions import *
from interactions.api.events import Startup
from Extensions.utilities import bot
from constants import *

class Rules(Extension):
	@Task.create(IntervalTrigger(hours=1))
	async def rules_task(self):

		channel = await bot.fetch_channel(RULES_CHANNEL_ID)

		async for previous_message in channel.history(limit=10):
			if not (previous_message.embeds and previous_message.embeds[0].title == RULES_EMBED.title and previous_message.author == self.bot.user):
				await previous_message.delete()
				await channel.send(embed=RULES_EMBED)

	@listen(Startup)
	async def on_startup(self, event: Startup):
		await self.rules_task()
		self.rules_task.start()
