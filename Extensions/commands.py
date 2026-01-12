from constants import *
from interactions import *

from Extensions.utilities import config, is_valid_uuid, create_embed

import whitelist_handler as whitelist

class Commands(Extension):
	@slash_command(
		name="whitelist_add",
		description="Add a member to server whitelist. ( Requires staff )",
		options=[
			SlashCommandOption(
				name="mc_username",
				description="Minecraft username.",
				type=OptionType.STRING,
				required=True,
			),
			SlashCommandOption(
				name="discord_user",
				description="Discord User",
				type=OptionType.USER,
				required=True,
			),
			SlashCommandOption(
				name="whitelist_file",
				description="Whitelist to remove the user from.",
				type=OptionType.STRING,
				required=True,
				choices=[	
							SlashCommandChoice(
								"staff", "staff.whitelist"
							),
							SlashCommandChoice(
								"event", "event.whitelist"
							)
						]
			)
		],
	)
	async def whitelist_add(self, ctx: ComponentContext, mc_username: str, discord_user: User, whitelist_file: str):
		await ctx.defer(ephemeral=False)

		role = ctx.guild.get_role(config.get_setting("staff_role_id", ""))
		if role in ctx.author.roles:
			mc_uuid, mc_name = whitelist.get_minecraft_account(mc_username)

			if mc_uuid and is_valid_uuid(mc_uuid):
				whitelist_user = whitelist.create_user(discord_user.id, discord_user.username, mc_uuid, mc_name)

				if whitelist.add_user(whitelist_user, whitelist_file):
					await ctx.send(
						embed=create_embed(
							f"Success...",
							f"Added {mc_name} to the whitelist.",
							0x00FF00
						)
						, ephemeral=True
					)
				else:
					await ctx.send(
						embed=create_embed(
							f"Failed...",
							f"{mc_name} is already whitelisted.",
							0xFFFF00
						)
						, ephemeral=True
					)
			else:
				await ctx.send(
					embed=create_embed(
						"Invalid account!",
						"We weren't able to find a minecraft account with this username, check your spelling and try again.",
						0xFF0000
					)
					, ephemeral=True
				)
		else:
			await ctx.send(
				embed=create_embed(
					"No permission!",
					"You can't run this command without the Staff role.",
					0xFF0000
				)
				, ephemeral=True
			)

	@slash_command(
		name="whitelist_remove",
		description="Removes a member from server whitelist. ( Requires staff )",
		options=[
			SlashCommandOption(
				name="mc_username",
				description="Minecraft username.",
				type=OptionType.STRING,
				required=True,
			),
			SlashCommandOption(
				name="discord_user",
				description="Discord User",
				type=OptionType.USER,
				required=True,
			),
			SlashCommandOption(
				name="whitelist_file",
				description="Whitelist to remove the user from.",
				type=OptionType.STRING,
				required=True,
				choices=[	
							SlashCommandChoice(
								"staff", "staff.whitelist"
							),
							SlashCommandChoice(
								"event", "event.whitelist"
							)
						]
			)
		],
	)
	async def whitelist_remove(self, ctx: ComponentContext, mc_username: str, discord_user: User, whitelist_file: str):
		await ctx.defer(ephemeral=False)

		role = ctx.guild.get_role(config.get_setting("staff_role_id", ""))
		if role in ctx.author.roles:
			mc_uuid, mc_name = whitelist.get_minecraft_account(mc_username)

			if mc_uuid and is_valid_uuid(mc_uuid):
				if whitelist.remove_user(mc_uuid, whitelist_file):
					await ctx.send(
						embed=create_embed(
							f"Success...",
							f"Removed {mc_name} from the whitelist.",
							0x00FF00
						)
						, ephemeral=True
					)
				else:
					await ctx.send(
						embed=create_embed(
							f"Failed...",
							f"{mc_name}, {discord_user.username} isn't whitelisted.",
							0xFFFF00
						)
						, ephemeral=True
					)
			else:
				await ctx.send(
					embed=create_embed(
						"Invalid account!",
						"We weren't able to find a minecraft account with this username, check your spelling and try again.",
						0xFF0000
					)
					, ephemeral=True
				)
		else:
			await ctx.send(
				embed=create_embed(
					"No permission!",
					"You can't run this command without the Staff role.",
					0xFF0000
				)
				, ephemeral=True
			)

	
