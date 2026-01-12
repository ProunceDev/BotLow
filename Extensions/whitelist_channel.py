from interactions import *
from constants import *

from asyncio import sleep
from interactions.api.events import MessageCreate
from Extensions.utilities import config, create_embed, is_valid_uuid, bot
import whitelist_handler as whitelist

class WhitelistChannel(Extension):
	@listen(MessageCreate)
	async def on_message_create(self, event: MessageCreate):
		whitelist_log_channel = await bot.fetch_channel(config.get_setting("staff_whitelist_log_channel", ""))

		if event.message.channel.id != int(config.get_setting("whitelist_channel", "")) or event.message.author.id == bot.user.id:
			return
		if not event.message.content.startswith("!whitelist "):
			await event.message.delete()
			return
		username = event.message.content.replace("!whitelist ", "")
		num_whitelisted = whitelist.get_number_of_whitelisted_users(event.message.author.id, "event.whitelist")
		if num_whitelisted > 0:
			await event.message.add_reaction("❌")
			reply = await event.message.reply(embed=create_embed(f"Failed...", f"You already whitelisted **{num_whitelisted}**, the maximum is **1**.", 0xFF0000))
			await whitelist_log_channel.send(embed=create_embed(f"Whitelist Log", f"**{event.message.author.username}** attempted to whitelist **{username}** but has already whitelisted **{num_whitelisted}** person(s)", 0xFFFF00))
			return

		mc_uuid, mc_name = whitelist.get_minecraft_account(username)

		if mc_uuid and is_valid_uuid(mc_uuid):
			whitelist_user = whitelist.create_user(event.message.author.id, event.message.author.username, mc_uuid, mc_name)

			if whitelist.add_user(whitelist_user, "event.whitelist"):
				await event.message.add_reaction("✅")
				reply = await event.message.reply(embed=create_embed(f"Success", f"**{mc_name}** is now whitelisted.", 0x00FF00))
				await whitelist_log_channel.send(embed=create_embed(f"Whitelist Log", f"**{event.message.author.username}** whitelisted **{mc_name}**.", 0xFFFFFF))
			else:
				await event.message.add_reaction("❌")
				reply = await event.message.reply(embed=create_embed(f"Failed...", f"**{mc_name}** is already whitelisted.", 0xFF0000))
				await whitelist_log_channel.send(embed=create_embed(f"Whitelist Log", f"**{event.message.author.username}** tried to whitelist **{mc_name}**, but they were already whitelisted.", 0xFFFF00))
		else:
			await event.message.add_reaction("❌")
			reply = await event.message.reply(embed=create_embed(f"Invalid account!", f"We weren't able to find a minecraft account with this username, check your spelling and try again.", 0xFF0000))
			await whitelist_log_channel.send(embed=create_embed(f"Whitelist Log", f"**{event.message.author.username}** tried to whitelist **{username}**, but it was an invalid account.", 0xFFFF00))
