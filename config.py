import os

# Load numerical IDs and cast them to integers
API_ID = int(os.environ.get("API_ID", 0))
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 0))

# Load string-based secrets
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")

# The BASE_URL is critical for link generation
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
