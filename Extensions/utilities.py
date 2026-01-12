from constants import *
from interactions import *
from bot_token import TOKEN
from settings import SettingsManager
import re

bot = Client(debug_scope=GUILD_ID, intents=Intents.ALL, token=TOKEN)
config = SettingsManager("config.json")

class Utilities(Extension):
	pass

def create_embed(title, description, color=0xFFFFFF):
		return Embed(title=title, description=description, color=color)

def is_valid_uuid(uuid):
	"""Check if the UUID is a valid 32-character hex string"""
	return bool(re.fullmatch(r"^[a-fA-F0-9]{32}$", uuid))