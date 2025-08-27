import os, glob
from interactions import *

ext_filenames = glob.glob(os.path.join("Extensions", "**", "*.py"), recursive=True)
EXTENSIONS = [os.path.splitext(filename)[0].replace(os.path.sep, ".") for filename in ext_filenames]

TRAPPING_CLIPS_CHANNEL_ID = 1308489572166009003
GUILD_ID = 1174401155128889374
RULES_CHANNEL_ID = 1215432855379775540
ANNOUNCEMENTS_CHANNEL_ID = 1174964254126915614
REACTION_ROLES_CHANNEL_ID = 1189332896729796688
CHANNEL_VIDEOS_URL = "https://www.youtube.com/@JudeLoSasso/videos"
CHANNEL_SHORTS_URL = "https://www.youtube.com/@JudeLoSasso/shorts"

SQUEAKER_ROLE_ID = 1174401617219555389
TRAPPER_ROLE_ID = 1174401711662714980
GOON_ROLE_ID = 1174401521178398904
LFT_ROLE_ID = 1189340890565713940
GAME_NIGHT_ROLE_ID = 1409989985066815593

REACTION_ROLES = {
					"🗣️": SQUEAKER_ROLE_ID,
					"😎": GOON_ROLE_ID,
					"🥸": TRAPPER_ROLE_ID,
					"❤": LFT_ROLE_ID,
					"🎮": GAME_NIGHT_ROLE_ID
				}

RULES_EMBED = Embed(
    title="Rules", 
    description="""
				> 1️⃣ **No Slurs** ➝ Using slurs or offensive language is strictly prohibited.

				> 2️⃣ **No Doxxing** ➝ Do not share anyone's personal information.

				> 3️⃣ **No Encouragement of Self-Harm** ➝ Encouraging anyone to "kys" or similar behavior is not allowed.

				> 4️⃣ **No Hacking Promotion** ➝ Promoting hacking, cheats, or exploits is forbidden.

				> 5️⃣ **Don't Be a Dickhead** ➝ Treat everyone with respect; toxic behavior is not tolerated.

				> 6️⃣ **No Unnecessary Pings** ➝ Avoid pinging the 'Big Boy' ranks without valid reasons.

				> 7️⃣ **Respect Staff Decisions** ➝ Staff actions are final; do not look for loopholes.
				""",
    color=BrandColors.BLURPLE
)

REACTION_ROLES_EMBED = Embed(
    title="Reaction Roles", 
    description="""
				> 🗣️ **Squeaker** ➝ Have a voice that sounds like a child.

				> 😎 **Goon** ➝ Skilled at acquiring resources and excelling in PvP.

				> 🥸 **Trapper** ➝ Familiar with the current trapping meta and strategies.

				> ❤ **LFT** ➝ Be notified when players are looking for teammates.

				> 🎮 **Game Night Ping** -> Be notified about staff sanctioned game nights.
				""",
    color=BrandColors.BLURPLE
)
