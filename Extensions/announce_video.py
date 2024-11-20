from interactions import *
from interactions.api.events import Startup
from Extensions.utilities import config, bot
from constants import *
import requests
from bs4 import BeautifulSoup

class AnnounceVideo(Extension):
	@Task.create(IntervalTrigger(seconds=30))
	async def announce_task(self):
			session = requests.Session()
			response = session.get(CHANNEL_VIDEOS_URL)
			soup = BeautifulSoup(response.text, "html.parser")

			titles = str(soup.prettify('utf-8')).split('"watchEndpoint":{"videoId":"')
			latest_video_id = titles[1].split('","watchEndpointSupportedOnesieConfig"')[0]
			
			if config.get_setting("latest_video_id", "") != latest_video_id:
				channel = await bot.fetch_channel(ANNOUNCEMENTS_CHANNEL_ID)
				await channel.send(f"New JudeLow upload! Go check it out over at https://www.youtube.com/watch?v={latest_video_id} @everyone")
				config.set_setting("latest_video_id", latest_video_id)

			response = session.get(CHANNEL_SHORTS_URL)
			soup = BeautifulSoup(response.text, "html.parser")

			titles = str(soup.prettify('utf-8')).split('{"videoId":"')
			latest_short_id = titles[1].split('","playerParams":"')[0]
			
			if config.get_setting("latest_short_id", "") != latest_short_id:
				channel = await bot.fetch_channel(ANNOUNCEMENTS_CHANNEL_ID)
				await channel.send(f"New JudeLow upload! Go check it out over at https://www.youtube.com/shorts/{latest_short_id} @everyone")
				config.set_setting("latest_short_id", latest_short_id)

	@listen(Startup)
	async def on_startup(self, event: Startup):
		await self.announce_task()
		self.announce_task.start()
