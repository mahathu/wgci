from datetime import datetime
from urllib.parse import urljoin
import logging

import requests
from bs4 import BeautifulSoup


class Ad:
    def __init__(self, row):
        # rows that are actually ads (!= 7 rows) are filtered out in wgcompanyWatcher.py)
        self.td = row.select("td")

        self.url = self.td[2].find("a", recursive=False).get("href")
        self.is_valid = True

        if not self.url.startswith("/cgi-bin/wg.pl"):
            # z.B. Papiertiger (Werbung)
            logging.warning(f"There was an invalid ad URL: {self.url}")
            self.is_valid = False

        self.title = self.url.split("=")[-1]

    def parse_details_page(self):
        if not self.is_valid:
            return

        request_url = urljoin("http://www.wgcompany.de", self.url)
        logging.info(f"Requesting details page: {request_url}...")
        r = requests.get(request_url)
        soup = BeautifulSoup(r.text, "html.parser")

        posted_on = (
            soup.select_one("#content font").text.strip().removeprefix("Eintrag vom ")
        )

        self.posted_on = datetime.strptime(posted_on, "%d. %B %Y").strftime("%Y-%m-%d")

        self.description = soup.find("blockquote").text.strip()
        self.available_from = (
            self.td[-1].get_text(strip=True).removeprefix("ab ").strip()
        )
        self.available_for = (
            soup.select_one('#content td:-soup-contains("Wie lange")')
            .find_next_sibling("td")
            .text.strip()
            .split()[0]
        )

        # get the desired age by ad authors:
        age_bracket = (  # Alter with a non-breaking space
            soup.find("td", string="Alter ").find_next_sibling().text.split("-")
        )
        # max_age has a default variable but min_age doesn't
        self.min_age = int(age_bracket[0]) if age_bracket[0].strip() else 0
        self.max_age = int(age_bracket[1])
        self.district = self.td[1].get_text(strip=True)
        self.rent = self.td[4].get_text(strip=True)[:-1]
        self.sqm = self.td[5].get_text(strip=True)[:-2]

    def __eq__(self, other) -> bool:
        return self.title == other.title

    def __repr__(self) -> str:
        return f"<Ad {self.title}>"

    def as_dict(self) -> dict:
        d = vars(self).copy()
        for key in ["td", "is_valid"][1:]:
            d.pop(key)
        return d

    def filter(self, filters: dict) -> dict:
        return {
            "desc": not any(
                [
                    word.lower() in self.description.lower()
                    for word in filters["desc_blacklist"]
                ]
            ),
            "age": self.min_age <= filters["user_age"] <= self.max_age,
            "district": self.district in filters["desired_districts"],
            "long_term": self.available_for == "dauerhaft",
        }

    def notify_telegram(self, api_token, chat_id):
        logging.info(f"Sending ad info to telegram: {self}")

        # raise NotImplementedError
