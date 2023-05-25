import html
import logging

import requests


class TelegramBot:
    def __init__(self, token: str, template: str):
        self.token = token
        self.template = template

    def notify_user(self, ad, chat_id):
        logging.info(f"Notifying {chat_id} about {ad}")
        api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        text = self.template.format(
            title=html.escape(ad.title),
            available_from=ad.available_from,
            district=ad.district,
            sqm=ad.sqm,
            rent=ad.rent,
            description=html.escape(ad.description),
            url=ad.url,
        )

        data = {"chat_id": chat_id, "text": text, "parse_mode": "html"}
        response = requests.post(api_url, data=data)
        if not response.ok:
            logging.error(f"Telegram response: {response.text} - Ad: {ad}")
