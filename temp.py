import discord
from discord.ext import commands
from datetime import datetime, timezone
import asyncio
from urllib.parse import urlparse

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

removed_reactions = {}

bot = commands.Bot(command_prefix="!", intents=intents)

def parse_message_link(link: str):
	parts = urlparse(link)
	segments = [seg for seg in parts.path.split("/") if seg]
	if len(segments) < 3:
		return None, None, None
	guild_id, channel_id, message_id = segments[-3:]
	try:
		return int(guild_id), int(channel_id), int(message_id)
	except ValueError:
		return None, None, None

async def remove_bot_reactions_from_links(message_links, cutoff_date: datetime):
	removed_count = 0
	for link in message_links:
		guild_id, channel_id, message_id = parse_message_link(link)
		if not channel_id or not message_id:
			print(f"Skipping invalid link: {link}")
			continue

		channel = bot.get_channel(channel_id)
		if not channel:
			print(f"Channel not found for link: {link}")
			continue

		try:
			msg = await channel.fetch_message(message_id)
		except Exception as e:
			print(f"Could not fetch message {message_id}: {e}")
			continue

		guild = channel.guild
		for reaction in msg.reactions:
			async for user in reaction.users():
				if user.bot:
					continue
				member = guild.get_member(user.id)
				if member is None:
					try:
						member = await guild.fetch_member(user.id)
					except Exception:
						continue
				if member.joined_at and member.joined_at > cutoff_date:
					removed_reactions[msg.content] = removed_reactions.get(msg.content, 0) + 1
					try:
						await reaction.remove(user)
						removed_count += 1
					except discord.Forbidden:
						print(f"No permission to remove reaction on {message_id}")
					except Exception as e:
						print(f"Error removing reaction on {message_id}: {e}")
	return removed_count

@bot.event
async def on_ready():
	print(f"{bot.user} has connected to Discord!")

async def main():
	async with bot:
		await bot.start("YOUR_BOT_TOKEN_HERE")

if __name__ == "__main__":
	@bot.event
	async def on_ready():
		print(f"{bot.user} has connected to Discord!")
		
		message_links = [
			"https://discord.com/channels/1174401155128889374/1174964254126915614/1455253716973260997",
			"https://discord.com/channels/1174401155128889374/1174964254126915614/1455250695459700779",
			"https://discord.com/channels/1174401155128889374/1174964254126915614/1455250815571853515",
			"https://discord.com/channels/1174401155128889374/1174964254126915614/1455251194011189309",
			"https://discord.com/channels/1174401155128889374/1174964254126915614/1455251427109765344",
			"https://discord.com/channels/1174401155128889374/1174964254126915614/1455251494545653800",
			"https://discord.com/channels/1174401155128889374/1174964254126915614/1455252336556507146",
			"https://discord.com/channels/1174401155128889374/1174964254126915614/1455252674290253967"
		]
		cutoff_date = datetime(2025, 12, 29, tzinfo=timezone.utc)

		try:
			removed = await remove_bot_reactions_from_links(message_links, cutoff_date)
			print(f"Removed {removed} reactions from the provided message links.")
			for msg_content, count in removed_reactions.items():
				print(f"Message: {msg_content} - Reactions Removed: {count}")
		except Exception as e:
			print(f"Error: {e}")
		finally:
			await bot.close()
	
	asyncio.run(main())