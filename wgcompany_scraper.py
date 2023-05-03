import os, json, requests, yaml, locale
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def generate_params_from_config(config):
    return {
        "st": "1",  # Verstecktes input-Feld, wenn es fehlt liefert zquery.pl ein leeres Ergebnis zurück
        "r": "1",  # Anzahl Zimmer gesucht
        "g": [
            str(i)
            for i in range(config["n_rooms_range"][0], config["n_rooms_range"][1] + 1)
        ],  # WG-Größe
        "b": config["rent_range"][0],  # min rent
        "a": config["rent_range"][1],  # max rent
        "c": config["room_sqm_range"][0],  # min room size
        "d": config["room_sqm_range"][1],  # max room size
        # "v": "dauerhaft" if config["long_term"] else "bis 6 Monate",  # wie lange
        "p": config[
            "max_age"
        ],  # Nur WG-Angebote berücksichtigen, die nicht älter sind als max_age Tage
    }


def scrape_listings(params):
    query_url = urljoin(BASE_URL, "cgi-bin/zquery.pl")
    listings_request = requests.post(query_url, data=params)

    soup = BeautifulSoup(listings_request.text, "html.parser")
    ad_rows = [row for row in soup.find_all("tr") if len(row) == 7]

    recent_ads = []
    for row in ad_rows:
        # Filter invalid rows:
        td_elements = row.select("td")
        link_element = td_elements[2].find("a", recursive=False)
        if not link_element or not link_element.get("href").startswith(
            "/cgi-bin/wg.pl"
        ):
            print("ERROR: link element missing or invalid")
            with open("error.html", "w") as error_file:
                error_file.write(row.prettify())

            continue

        # merge dicts:
        recent_ads.append(
            get_data_from_row_element(row)
            | get_detail_from_ad_url(link_element.get("href"))
        )

    return recent_ads


def get_data_from_row_element(row):
    td_elements = row.select("td")

    return {
        "district": td_elements[1].get_text(strip=True),
        "available_from": td_elements[-1]
        .get_text(strip=True)
        .removeprefix("ab ")
        .strip(),
        "rent": td_elements[4].get_text(strip=True)[:-1],
        "sqm": td_elements[5].get_text(strip=True)[:-2],
        "deleted": False,
    }


def get_detail_from_ad_url(url):
    r = requests.get(urljoin(BASE_URL, url))
    soup = BeautifulSoup(r.text, "html.parser")

    posted_on = (
        soup.select_one("#content font").text.strip().removeprefix("Eintrag vom ")
    )
    posted_on_iso_str = datetime.strptime(posted_on, "%d. %B %Y").strftime("%Y-%m-%d")

    description = soup.find("blockquote").text.strip()
    available_for = (
        soup.select_one('#content td:-soup-contains("Wie lange")')
        .find_next_sibling("td")
        .text.strip()
        .split()[0]
    )

    return {
        "title": url.split("=")[-1],
        "posted_on": posted_on_iso_str,
        "available_for": available_for,
        "description": description,
        "url": urljoin(BASE_URL, url),
        "filtered": any(w in description.lower() for w in CONFIG["filter_strings"]),
    }


def load_existing_ads(file_url):
    if os.path.isfile(file_url):
        with open(file_url, "r") as archive_file:
            return json.load(archive_file)
    return {}


if __name__ == "__main__":
    BASE_URL = "http://www.wgcompany.de/"

    # Set up:
    with open("config.yml", "r") as config_file:
        CONFIG = yaml.safe_load(config_file)

    params = generate_params_from_config(CONFIG)
    locale.setlocale(locale.LC_TIME, "de_DE")
    ads = load_existing_ads(CONFIG["archive_file"])
    n_ads_total = len(ads)

    while True:
        print("Started scraping...")

        published_ads = {ad["title"]: ad for ad in scrape_listings(params)}

        # if a previously found ad is not in the new results, flag it as deleted:
        deleted_ads = ads.keys() - published_ads.keys()
        for title in deleted_ads:
            print(f"{title} was deleted")
            ads[title]["deleted"] = True

        # overwrite existing ads:
        ads.update(published_ads)

        print(
            f"{len(published_ads)} ads found (+{len(ads) - n_ads_total}/-{len(deleted_ads)})"
        )
        n_ads_total = len(ads)

        # write everything back to file:
        with open(CONFIG["archive_file"], "w") as archive_file:
            json.dump(ads, archive_file, ensure_ascii=False, indent=2)
            print(f"Updated {CONFIG['archive_file']}.")

        break
        # sleep for 15 minutes
