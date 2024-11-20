from constants import *
from interactions import *
from bot_token import TOKEN
from settings import SettingsManager

bot = Client(debug_scope=GUILD_ID, intents=Intents.ALL, token=TOKEN)
config = SettingsManager("config.json")

class Utilities(Extension):
	pass