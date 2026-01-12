from constants import *
from interactions import *
from interactions.ext import prefixed_commands
from Extensions.utilities import bot
from network_api import app
import threading

prefixed_commands.setup(bot, default_prefix="=")

@listen()
async def on_ready():
	print("Ready")
	print(f"Logged in as {bot.user}")

for extension in EXTENSIONS:
	bot.load_extension(extension)

def run_flask():
    app.run(host="0.0.0.0", port=5050, threaded=True)

if __name__ == "__main__":
	flask_thread = threading.Thread(target=run_flask, daemon=True)
	flask_thread.start()

	bot.start()
