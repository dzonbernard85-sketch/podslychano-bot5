# config.py
import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

STUDENT_BOT_TOKEN = os.getenv("STUDENT_BOT_TOKEN")
MODERATOR_BOT_TOKEN = os.getenv("MODERATOR_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = os.getenv("CHANNEL_ID")