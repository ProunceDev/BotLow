import os, glob
from interactions import *

ext_filenames = glob.glob(os.path.join("Extensions", "**", "*.py"), recursive=True)
EXTENSIONS = [os.path.splitext(filename)[0].replace(os.path.sep, ".") for filename in ext_filenames]

TRAPPING_CLIPS_CHANNEL_ID = 1308489572166009003
GUILD_ID = 1174401155128889374
RULES_CHANNEL_ID = 1215432855379775540
ANNOUNCEMENTS_CHANNEL_ID = 1174964254126915614
CHANNEL_VIDEOS_URL = "https://www.youtube.com/@JudeLoSasso/videos"
CHANNEL_SHORTS_URL = "https://www.youtube.com/@JudeLoSasso/shorts"

RULES_EMBED = Embed(title="Rules", 
					description="""**Rule 1**: No Slurs\n**Rule 2**: No Doxxing\n**Rule 3**: Do not encourage people to "kys"\n**Rule 4**: Do not promote hacking.\n**Rule 5**: Do not be a dickhead\n**Rule 6**: Do not ping any of the 'Big Boy' ranks.\n**Rule 7**: Staff punish as they see fit, don't try to find loopholes.""", 
					color=BrandColors.GREEN)