from interactions import *
from interactions.api.events import MessageCreate
from constants import *

class Trapping_Clips(Extension):
	@listen(MessageCreate)
	async def on_message_create(self, event: MessageCreate):
		if event.message.channel.id != TRAPPING_CLIPS_CHANNEL_ID:
			return

		if not event.message.attachments and not "https://" in event.message.content:
			return
		
		try:
			await event.message.add_reaction("👍")
			await event.message.add_reaction("👎")
		except Exception as e:
			print(f"Failed to add reactions: {e}")

		try:
			await event.message.create_thread(name=f"Clip | {event.message.author.display_name}", auto_archive_duration=10080)
		except Exception as e:
			print(f"Failed to create thread: {e}")