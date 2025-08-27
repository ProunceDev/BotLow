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

		existing_message = None

		async for previous_message in channel.history(limit=10):
			# Only check messages by the bot with an embed
			if previous_message.author == self.bot.user and previous_message.embeds:
				existing_embed = previous_message.embeds[0]

				# Compare titles (and optionally other fields)
				if existing_embed.title == REACTION_ROLES_EMBED.title:
					# If embed is different, edit it
					if existing_embed.to_dict() != REACTION_ROLES_EMBED.to_dict():
						await previous_message.edit(embed=REACTION_ROLES_EMBED)
					existing_message = previous_message
					break

			# If message is not the reaction roles message, delete it
			await previous_message.delete()

		# If no valid embed found, send a new one
		if existing_message == None:
			existing_message = await channel.send(embed=REACTION_ROLES_EMBED)

		try:
			await existing_message.add_reaction("🗣️")
			await existing_message.add_reaction("😎")
			await existing_message.add_reaction("🥸")
			await existing_message.add_reaction("❤")
			await existing_message.add_reaction("🎮")
		except Exception as e:
			print(f"Failed to add reactions: {e}")


	@listen(Startup)
	async def on_startup(self, event: Startup):
		await self.reaction_roles_task()
		self.reaction_roles_task.start()
