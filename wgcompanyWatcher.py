import time
import logging

import requests
from bs4 import BeautifulSoup
import pandas as pd
import yaml

from ad import Ad
from telegram import TelegramBot


class WGCompanyWatcher:
    def __init__(self):
        # Load config
        with open("config.yml", "r") as config_file:
            self.config = yaml.safe_load(config_file)
        with open("secrets.yml", "r") as secrets_file:
            self.secrets = yaml.safe_load(secrets_file)
        with open("telegram-notification-template.html", "r") as template_file:
            tg_message_template = template_file.read()

        self.telegram_bot = TelegramBot(
            token=self.secrets["telegram"]["bot_token"], template=tg_message_template
        )

        try:
            self.ads = pd.read_csv(self.config["archive_file"])
        except (FileNotFoundError, pd.errors.EmptyDataError):
            self.ads = pd.DataFrame(columns=["url"])

        logging.info(f"App initialized ({len(self.ads)} archived ads)")

    def _get_current_listings(self):
        query_url = "http://www.wgcompany.de/cgi-bin/zquery.pl"
        search_params = {
            "st": "1",  # Verstecktes input- Feld, wenn es fehlt liefert zquery.pl ein leeres Ergebnis zurück
            "r": "1",  # Anzahl Zimmer gesucht
            "g": [
                str(i)
                for i in range(
                    self.config["n_rooms_range"][0], self.config["n_rooms_range"][1] + 1
                )
            ],  # WG - Größe
            "b": self.config["rent_range"][0],  # min rent
            "a": self.config["rent_range"][1],  # max rent
            "c": self.config["room_sqm_range"][0],  # min room size
            "d": self.config["room_sqm_range"][1],  # max room size
            "p": self.config["max_age"],
            # Nur WG - Angebote berücksichtigen, die nicht älter sind als max_age Tage
        }

        listings_request = requests.post(query_url, data=search_params)
        soup = BeautifulSoup(listings_request.text, "html.parser")

        ads = [Ad(row) for row in soup.find_all("tr") if len(row) == 7]
        return [ad for ad in ads if ad.is_valid]

    def run(self, interval=600):
        logging.info("App is running 🚀")
        while True:
            current_ads = self._get_current_listings()

            new_ads = [ad for ad in current_ads if ad.url not in self.ads["url"].values]

            logging.info(
                f"online: {len(current_ads)}, new: {len(new_ads)}, total: {len(self.ads) + len(new_ads)}"
            )

            for ad in new_ads:
                ad.parse_details_page()

                # A valid ad has "True" for all of these filters:
                ad_filters = ad.filter(self.config["filters"])

                # If ad matches criteria, notify via telegram:
                if all(ad_filters.values()):
                    self.telegram_bot.notify_user(
                        ad, chat_id=self.secrets["telegram"]["chat_id"]
                    )

            # Save ads to file:
            if new_ads:
                # append new_ads to ads:
                new_ads_df = pd.DataFrame([ad.as_dict() for ad in new_ads])
                self.ads = pd.concat([self.ads, new_ads_df], ignore_index=True)
                self.ads.to_csv(self.config["archive_file"], index=False)

            time.sleep(interval)
