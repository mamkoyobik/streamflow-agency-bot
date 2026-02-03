import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")



if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден")
if not CHANNEL_ID:
    raise RuntimeError("❌ CHANNEL_ID не найден")
