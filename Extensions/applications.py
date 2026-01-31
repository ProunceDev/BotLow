from interactions import *
from Extensions.utilities import config, bot
from constants import *
import aiosqlite, json

applications_in_progress = {}
application_temp = {}

class Applications(Extension):
	status_message_id = 0

	async def init_db(self):
		async with aiosqlite.connect("applications.db") as db:
			await db.execute("""
				CREATE TABLE IF NOT EXISTS applications (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					data TEXT,
					status TEXT,
					user_id INTEGER
				)
			""")

			await db.commit()

	async def set_application_status(self, application_id: int, status: str):
		async with aiosqlite.connect("applications.db") as db:
			await db.execute("UPDATE applications SET status = ? WHERE id = ?", (status, application_id))
			await db.commit()

	async def has_applied(self, user_id: int) -> bool:
		async with aiosqlite.connect("applications.db") as db:
			async with db.execute("SELECT 1 FROM applications WHERE user_id = ? LIMIT 1", (user_id,)) as cursor:
				return await cursor.fetchone() is not None
			
	async def get_total_applications(self):
		async with aiosqlite.connect("applications.db") as db:
			async with db.execute("SELECT COUNT(*) FROM applications") as cursor:
				return (await cursor.fetchone())[0]

	async def get_unviewed_applications(self):
		async with aiosqlite.connect("applications.db") as db:
			async with db.execute("SELECT COUNT(*) FROM applications WHERE status IS NULL") as cursor:
				return (await cursor.fetchone())[0]

	async def get_accepted_applications(self):
		async with aiosqlite.connect("applications.db") as db:
			async with db.execute("SELECT COUNT(*) FROM applications WHERE status = 'ACCEPTED'") as cursor:
				return (await cursor.fetchone())[0]

	async def get_denied_applications(self):
		async with aiosqlite.connect("applications.db") as db:
			async with db.execute("SELECT COUNT(*) FROM applications WHERE status = 'DENIED'") as cursor:
				return (await cursor.fetchone())[0]
			
	async def get_next_application(self, current_id: int):
		# Get the next application with ID greater than current_id and status NULL
		async with aiosqlite.connect("applications.db") as db:
			async with db.execute("SELECT id, data FROM applications WHERE id > ? AND status IS NULL ORDER BY id ASC LIMIT 1", (current_id,)) as cursor:
				row = await cursor.fetchone()
				return row if row else None
			
	async def get_application_by_id(self, app_id: int):
		async with aiosqlite.connect("applications.db") as db:
			async with db.execute("SELECT id, data FROM applications WHERE id = ?", (app_id,)) as cursor:
				row = await cursor.fetchone()
				return row if row else None
	
	async def move_application_to_back(self, application_id: int):
		async with aiosqlite.connect("applications.db") as db:
			async with db.execute("SELECT MAX(id) FROM applications") as cursor:
				max_id = (await cursor.fetchone())[0] or 0
			new_id = max_id + 1
			await db.execute("UPDATE applications SET id = ? WHERE id = ?", (new_id, application_id))
			await db.commit()

	async def delete_application(self, application_id: int):
		async with aiosqlite.connect("applications.db") as db:
			await db.execute("DELETE FROM applications WHERE id = ?", (application_id,))
			await db.commit()

		# update all IDs greater than the deleted one to fill the gap
		async with aiosqlite.connect("applications.db") as db:
			await db.execute("UPDATE applications SET id = id - 1 WHERE id > ?", (application_id,))
			await db.commit()

	async def get_application_by_id(self, app_id: int):
		async with aiosqlite.connect("applications.db") as db:
			async with db.execute("SELECT id, data FROM applications WHERE id = ?", (app_id,)) as cursor:
				row = await cursor.fetchone()
				return row if row else None

	def build_application_embed(self, data: dict, username: str, id: str) -> Embed:
		embed = Embed(title=f"{username}'s Application", description=f"Reviewing application #{id}", color=0x00ff99)

		for i, question in enumerate(QUESTIONS, start=1):
			answer = data.get(str(i), "N/A")
			embed.add_field(name=f"{i}. {question}", value=str(answer), inline=False)

		return embed
	
	@slash_command(
		name="view_applications",
		description="Send the application viewer embed."
	)
	async def view_applications(self, ctx: SlashContext):
		await ctx.defer()
		role = ctx.guild.get_role(config.get_setting("staff_role_id", ""))
		role2 = ctx.guild.get_role(config.get_setting("mod_role_id", ""))
		if role in ctx.author.roles or role2 in ctx.author.roles:
			current_id = int(config.get_setting("current_application_id", "0"))

			next_app = await self.get_next_application(current_id)

			if next_app:
				current_id, data = next_app

				data = dict(json.loads(data))
				
				embed = self.build_application_embed(data, data.get("0", {"name":"N/A"})["name"], str(current_id))

				buttons = [
					Button(style=ButtonStyle.DANGER, label="Deny", custom_id="application_deny"),
					Button(style=ButtonStyle.SUCCESS, label="Accept", custom_id="application_accept"),
					Button(style=ButtonStyle.SECONDARY, label="Push to back", custom_id="application_delay")
				]

				await ctx.send(embed=embed, components=buttons)

			else:
				await ctx.send(
					embed=Embed(
						"No more applications to view!",
						"",
						0xFF0000
					)
				)
		else:
			await ctx.send(
				embed=Embed(
					"No permission!",
					"You can't run this command without the Staff role.",
					0xFF0000
				)
				, ephemeral=True
			)

	@slash_command(
		name="application_delete",
		description="Delete an application by its ID.",
		options=[
			SlashCommandOption(
				name="application_id",
				description="The ID of the application to delete.",
				type=OptionType.INTEGER,
				required=True
			)
		]
	)
	async def application_delete(self, ctx: SlashContext, application_id: int):
		await ctx.defer()
		role = ctx.guild.get_role(config.get_setting("staff_role_id", ""))
		role2 = ctx.guild.get_role(config.get_setting("mod_role_id", ""))
		if role in ctx.author.roles or role2 in ctx.author.roles:
			app = await self.get_application_by_id(application_id)
			if not app:
				await ctx.send(
					embed=Embed(
						"Application Not Found",
						f"No application found with ID #{application_id}.",
						0xFF0000
					)
				)
				return
			data = dict(json.loads(app[1]))
			user_id = data.get("0", {"id":"N/A"})["id"]
			try:
				member = await ctx.guild.fetch_member(user_id)
				embed = Embed(
					title="Application Deleted",
					description=f"Your application for the JudeLowSMP has been deleted by staff. You may now reapply if you wish.",
					color=0xFF0000
				)
				await member.send(embed=embed)
			except:
				pass
			await self.delete_application(application_id)
			await ctx.send(
				embed=Embed(
					"Application Deleted",
					f"Successfully deleted application #{application_id}.",
					0x00FF00
				)
			)
		else:
			await ctx.send(
				embed=Embed(
					"No permission!",
					"You can't run this command without the Staff role.",
					0xFF0000
				)
				, ephemeral=True
			)

	@component_callback("application_deny")
	async def deny_button(self, ctx: ComponentContext):
		await ctx.defer()
		role = ctx.guild.get_role(config.get_setting("staff_role_id", ""))
		role2 = ctx.guild.get_role(config.get_setting("mod_role_id", ""))
		if role in ctx.author.roles or role2 in ctx.author.roles:
			application_id = int(ctx.message.embeds[0].description.split("#")[1])
			await self.set_application_status(application_id, "DENIED")
			await ctx.channel.send(embed=Embed(f"Denied application #{application_id}", "Sending next application", 0xFF0000))
			await ctx.message.delete()

			next_app = await self.get_next_application(application_id)

			if next_app:
				current_id, data = next_app

				config.set_setting("current_application_id", str(current_id))

				data = dict(json.loads(data))
				embed = Embed(
					title="Application Viewer",
					description=f"Reviewing application #{current_id}",
					color=0x3498db
				)

				embed = self.build_application_embed(data, data.get("0", {"name":"N/A"})["name"], str(current_id))

				buttons = [
					Button(style=ButtonStyle.DANGER, label="Deny", custom_id="application_deny"),
					Button(style=ButtonStyle.SUCCESS, label="Accept", custom_id="application_accept"),
					Button(style=ButtonStyle.SECONDARY, label="Push to back", custom_id="application_delay")
				]

				await ctx.channel.send(embed=embed, components=buttons)

			else:
				await ctx.channel.send(
					embed=Embed(
						"No more applications to view!",
						"",
						0xFF0000
					)
				)
		else:
			await ctx.send(
				embed=Embed(
					"No permission!",
					"You can't run this command without the Staff role.",
					0xFF0000
				)
				, ephemeral=True
			)

	@component_callback("application_accept")
	async def accept_button(self, ctx: ComponentContext):
		await ctx.defer()
		role = ctx.guild.get_role(config.get_setting("staff_role_id", ""))
		role2 = ctx.guild.get_role(config.get_setting("mod_role_id", ""))
		if role in ctx.author.roles or role2 in ctx.author.roles:
			application_id = int(ctx.message.embeds[0].description.split("#")[1])
			await self.set_application_status(application_id, "ACCEPTED")
			await ctx.channel.send(embed=Embed(f"Accepted application #{application_id}", "Sending next application", 0x00FF00))
			await ctx.message.delete()

			current_app = await self.get_application_by_id(application_id)

			if current_app:
				current_id, data = current_app

				data = dict(json.loads(data))

				current_event_role_id = int(config.get_setting("current_event_role_id"))

				current_event_role = await ctx.guild.fetch_role(current_event_role_id)

				application_member = await ctx.guild.fetch_member(data.get("0", {"id":1170232393752387696})["id"])

				try:
					await application_member.add_role(current_event_role)

					embed = Embed(
							title="Application Accepted!",
							description=f"Your application for the JudeLowSMP was accepted! Make sure to check out https://discord.com/channels/1174401155128889374/1460298062139232472 for information regarding the server.",
							color=0x3498db
						)

					await application_member.send(embed=embed)
				except:
					pass

				next_app = await self.get_next_application(application_id)

				if next_app:
					current_id, data = next_app

					config.set_setting("current_application_id", str(current_id))

					data = dict(json.loads(data))
					embed = Embed(
						title="Application Viewer",
						description=f"Reviewing application #{current_id}",
						color=0x3498db
					)

					embed = self.build_application_embed(data, data.get("0", {"name":"N/A"})["name"], str(current_id))

					buttons = [
						Button(style=ButtonStyle.DANGER, label="Deny", custom_id="application_deny"),
						Button(style=ButtonStyle.SUCCESS, label="Accept", custom_id="application_accept"),
						Button(style=ButtonStyle.SECONDARY, label="Push to back", custom_id="application_delay")
					]

					await ctx.channel.send(embed=embed, components=buttons)

				else:
					await ctx.channel.send(
						embed=Embed(
							"No more applications to view!",
							"",
							0xFF0000
						)
					)
			
			else:
				await ctx.channel.send(
					embed=Embed(
						"Invalid application.",
						"",
						0xFF0000
					)
				)
		else:
			await ctx.send(
				embed=Embed(
					"No permission!",
					"You can't run this command without the Staff role.",
					0xFF0000
				)
				, ephemeral=True
			)

	@component_callback("application_delay")
	async def delay_button(self, ctx: ComponentContext):
		await ctx.defer()
		role = ctx.guild.get_role(config.get_setting("staff_role_id", ""))
		role2 = ctx.guild.get_role(config.get_setting("mod_role_id", ""))
		if role in ctx.author.roles or role2 in ctx.author.roles:
			application_id = int(ctx.message.embeds[0].description.split("#")[1])
			#await self.move_application_to_back(application_id)
			await ctx.channel.send(embed=Embed(f"Pushed application #{application_id} to the back.", "Sending next application", 0xFF0000))
			await ctx.message.delete()

			next_app = await self.get_next_application(application_id)

			if next_app:
				current_id, data = next_app

				config.set_setting("current_application_id", str(current_id))

				data = dict(json.loads(data))
				embed = Embed(
					title="Application Viewer",
					description=f"Reviewing application #{current_id}",
					color=0x3498db
				)

				embed = self.build_application_embed(data, data.get("0", {"name":"N/A"})["name"], str(current_id))

				buttons = [
					Button(style=ButtonStyle.DANGER, label="Deny", custom_id="application_deny"),
					Button(style=ButtonStyle.SUCCESS, label="Accept", custom_id="application_accept"),
					Button(style=ButtonStyle.SECONDARY, label="Push to back", custom_id="application_delay")
				]

				await ctx.channel.send(embed=embed, components=buttons)

			elif await self.get_unviewed_applications() > 0:
				# wrap around to the first application
				next_app = await self.get_next_application(0)

				if next_app:
					current_id, data = next_app

					config.set_setting("current_application_id", str(current_id))

					data = dict(json.loads(data))
					embed = Embed(
						title="Application Viewer",
						description=f"Reviewing application #{current_id}",
						color=0x3498db
					)

					embed = self.build_application_embed(data, data.get("0", {"name":"N/A"})["name"], str(current_id))

					buttons = [
						Button(style=ButtonStyle.DANGER, label="Deny", custom_id="application_deny"),
						Button(style=ButtonStyle.SUCCESS, label="Accept", custom_id="application_accept"),
						Button(style=ButtonStyle.SECONDARY, label="Push to back", custom_id="application_delay")
					]

					await ctx.channel.send(embed=embed, components=buttons)

			else:
				await ctx.channel.send(
					embed=Embed(
						"No more applications to view!",
						"",
						0xFF0000
					)
				)
		else:
			await ctx.send(
				embed=Embed(
					"No permission!",
					"You can't run this command without the Staff role.",
					0xFF0000
				)
				, ephemeral=True
			)

	@listen()
	async def on_message_create(self, event):
		message = event.message

		if not message.author.bot and message.guild is not None:
			if "!apply" in message.content.lower() or "@botlow" in message.content.lower() or "<@1308532022569996309>" in message.content.lower():
				await message.channel.send("Hi there! To apply for the JudeLowSMP, please **direct message** me with **!apply** to start the application process.")

		if message.author.bot or message.guild is not None:
			return

		user_id = message.author.id
		progress = applications_in_progress.get(user_id, 0)

		if message.content == "!cancel":
			if progress > 0:
				await message.channel.send("Application canceled.")
				applications_in_progress[user_id] = 0
				return
			else:
				await message.channel.send("You are not actively applying.")
				return

		if message.content != "!apply" and progress < 1:
			if await self.has_applied(user_id):
				await message.channel.send("You've already applied for the JudeLowSMP, we will contact you if you are accepted. (Make sure your DMs are open.)")
				return
			else:
				await message.channel.send("If you are trying to apply for the JudeLowSMP, type **!apply** to start, and **!cancel** at any time to cancel.")
				return

		if message.content == "!apply":
			if progress > 0:
				await message.channel.send("You're already in the application process.")
				return
			if await self.has_applied(user_id):
				await message.channel.send("You've already applied for the JudeLowSMP, we will contact you if you are accepted. (Make sure your DMs are open.)\n-# If you would like to reapply, please contact a staff member.")
				return

			await message.channel.send('The application process has started. Say "Ready" when you are ready to start, and **!cancel** to cancel at any time.')
			application_temp[user_id] = {0: {"name": message.author.display_name, "id": user_id}}
			applications_in_progress[user_id] = 1
			return

		if message.content.lower() == "ready" and progress == 1:
			await message.channel.send(f"**(1/{len(QUESTIONS)})** {QUESTIONS[0]}")
			applications_in_progress[user_id] = 2
			return

		if progress > 1 and progress <= len(QUESTIONS) + 1:
			# make sure message is not longer then 500 characters
			if len(message.content) > 500:
				await message.channel.send("Your answer is too long, please keep it under 500 characters.")
				return
			
			# make sure message contains no attachments
			if len(message.attachments) > 0:
				await message.channel.send("Please do not send attachments, only text answers are allowed.")
				return
			
			# make sure all links contain youtube
			if "http://" in message.content or "https://" in message.content:
				if "youtube.com" not in message.content and "youtu.be" not in message.content:
					await message.channel.send("Please only send YouTube links for your application video.")
					return

			application_temp[user_id][progress - 1] = message.content
			if progress - 1 > len(QUESTIONS) - 1:
				applications_in_progress[user_id] = 0
				app_id = 0
				async with aiosqlite.connect("applications.db") as db:
					cursor = await db.execute(
						"INSERT INTO applications (data, user_id) VALUES (?, ?)",
						(json.dumps(application_temp[user_id]), user_id)
					)
					await db.commit()
					app_id = cursor.lastrowid

				await message.channel.send(f"✅ Thanks! Your application has been submitted. We’ll reach out if you're selected. (Make sure your DMs are open.) `Application ID: {app_id}`")
				
				return

			await message.channel.send(f"**({progress}/{len(QUESTIONS)})** {QUESTIONS[progress - 1]}")
			applications_in_progress[user_id] += 1

	async def build_application_status_embed(self):
		embed = Embed(
			title="Application Status",
			description="Current application statistics:",
			color=0x3498db
		)
		embed.add_field(name="Total", value=await self.get_total_applications(), inline=False)
		embed.add_field(name="Accepted", value=await self.get_accepted_applications(), inline=False)
		embed.add_field(name="Denied", value=await self.get_denied_applications(), inline=False)
		embed.add_field(name="Unviewed", value=await self.get_unviewed_applications(), inline=False)
		
		button = Button(
			style=ButtonStyle.PRIMARY, 
			label="View Applications", 
			custom_id="view_applications"
		)
		return embed, [button]

	@component_callback("view_applications")
	async def view_applications_button(self, ctx: ComponentContext):
		await self.view_applications(ctx)

	@Task.create(IntervalTrigger(minutes=1))
	async def update_embed(self):
		channel = await bot.fetch_channel(config.get_setting("application_viewer_channel_id"))
		if channel:
			async for message in channel.history(limit=1):
				message: Message
				if message and (Timestamp.utcnow().timestamp() - message.timestamp.timestamp()) >= 120:
					embed, components = await self.build_application_status_embed()
					if message.id == self.status_message_id:
						try:
							await message.edit(embed=embed, components=components)
						except errors.NotFound:
							message = await channel.send(embed=embed, components=components)
							self.status_message_id = message.id
					else:
						message = await channel.send(embed=embed, components=components)
						self.status_message_id = message.id
		else:
			print("No valid application viewer channel found, please update 'application_viewer_channel_id' in config.")

	@listen()
	async def on_ready(self):
		print("Starting tasks...")
		await self.init_db()
		await self.update_embed()
		self.update_embed.start()