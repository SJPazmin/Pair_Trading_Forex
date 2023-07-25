import requests
from decouple import config
import logging

# Setup configuration
bot_token = config("TELEGRAM_TOKEN")
chat_id = config("TELEGRAM_CHAT_ID")
api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

# Setup logging
logging.basicConfig(level=logging.INFO)


def send_message(message):
    # Sanitize message
    # Depending on your use case, this may need to be updated
    message = message.strip()

    try:
        res = requests.post(
            api_url, json={"chat_id": chat_id, "text": message})

        if res.status_code != 200:
            logging.error(f"Failed to send message: {res.text}")
            return False
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Exception occurred: {e}")
        return False


if __name__ == "__main__":
    send_message("Hello World!")
