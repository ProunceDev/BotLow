from constants import *
from interactions import *
from interactions.ext import prefixed_commands
from Extensions.utilities import bot

prefixed_commands.setup(bot, default_prefix="=")

@listen()
async def on_ready():
	print("Ready")
	print(f"Logged in as {bot.user}")

for extension in EXTENSIONS:
	bot.load_extension(extension)

if __name__ == "__main__":
	bot.start()
