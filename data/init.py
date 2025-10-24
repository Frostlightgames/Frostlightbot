import os

from dotenv import load_dotenv
from data.classes.database import DATABASE

load_dotenv()

def init():
    DATABASE.set_config("guild_id",os.getenv("GUILDID"))
    DATABASE.set_config("main_channel_id",os.getenv("MAIN_CHANNEL_ID"))
    DATABASE.set_config("sandbox_channel_id",os.getenv("SANDBOX_CHANNEL_ID"))
    DATABASE.set_config("log_channel_id",os.getenv("LOG_CHANNEL_ID"))
    DATABASE.set_config("main_member_role_id",os.getenv("MAIN_MEMBER_ROLE_ID"))
    DATABASE.set_config("halloween_chat_category",os.getenv("HALLOWEEN_CHAT_CATEGORY_ID"))
    DATABASE.set_config("halloween_looter_role",os.getenv("HALLOWEEN_LOOTER_ROLE_ID"))