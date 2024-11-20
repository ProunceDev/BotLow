from interactions import *
from interactions.api.events import MessageReactionAdd, MessageReactionRemove, Startup
from constants import *
from Extensions.utilities import bot

class ReactionHandler(Extension):
	@listen(MessageReactionAdd)
	async def on_reaction_add(self, event: MessageReactionAdd):
		message = event.message
		emoji = event.emoji.name
		author = event.author

		if not (message.embeds and message.embeds[0].title == REACTION_ROLES_EMBED.title and message.author == self.bot.user):
			return
		
		role_id = REACTION_ROLES[emoji]
		role = await message.guild.fetch_role(role_id)
		await author.add_role(role)

	@listen(MessageReactionRemove)
	async def on_reaction_remove(self, event: MessageReactionRemove):
		message = event.message
		emoji = event.emoji.name
		author = event.author

		if not (message.embeds and message.embeds[0].title == REACTION_ROLES_EMBED.title and message.author == self.bot.user):
			return
		
		role_id = REACTION_ROLES[emoji]
		role = await message.guild.fetch_role(role_id)
		await author.remove_role(role)
		
	@Task.create(IntervalTrigger(hours=1))
	async def reaction_roles_task(self):

		channel = await bot.fetch_channel(REACTION_ROLES_CHANNEL_ID)

		async for previous_message in channel.history(limit=10):
			if not (previous_message.embeds and previous_message.embeds[0].title == REACTION_ROLES_EMBED.title and previous_message.author == self.bot.user):
				await previous_message.delete()
				message = await channel.send(embed=REACTION_ROLES_EMBED)
						
				try:
					await message.add_reaction("🗣️")
					await message.add_reaction("😎")
					await message.add_reaction("🥸")
					await message.add_reaction("❤")
				except Exception as e:
					print(f"Failed to add reactions: {e}")

	@listen(Startup)
	async def on_startup(self, event: Startup):
		await self.reaction_roles_task()
		self.reaction_roles_task.start()
