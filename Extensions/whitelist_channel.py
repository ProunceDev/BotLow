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

	@Task.create(IntervalTrigger(minutes=1))
	async def update_roles(self):
		users = whitelist.load_users("event.whitelist")

		guild = bot.get_guild(int(config.get_setting("guild_id", "")))
		if guild is None:
			return

		ROLE_IDS = {
			"smp_access": 1460297298994008225,
			"booster": 1177279290577002608,
			"member": 1461521851816743005,
		}

		# Highest > lowest priority
		ROLE_PRIORITY = ["member", "booster", "smp_access"]

		for user in users:
			discord_id = int(user[0])
			mc_uuid = user[2]

			member = guild.get_member(discord_id)

			if member is None:
				continue  # User left server or not cached

			member_role_ids = {role.id for role in member.roles}

			assigned_role = None
			for role_name in ROLE_PRIORITY:
				if ROLE_IDS[role_name] in member_role_ids:
					assigned_role = role_name
					break

			whitelist.save_user_role(mc_uuid, assigned_role)

	@listen()
	async def on_ready(self):
		print("Starting role task...")
		await self.update_roles()
		self.update_roles.start()