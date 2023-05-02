import os, json, requests, yaml
from bs4 import BeautifulSoup
from urllib.parse import urljoin


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
        "archived": False,
    }


def get_detail_from_ad_url(url):
    r = requests.get(urljoin(BASE_URL, url))
    soup = BeautifulSoup(r.text, "html.parser")

    description = soup.find("blockquote").text.strip()

    return {
        "title": url.split("=")[-1],
        "description": description,
        "url": urljoin(BASE_URL, url),
        "filtered": any(w in description.lower() for w in CONFIG["filter_strings"]),
    }


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
        "v": "dauerhaft" if config["long_term"] else "bis 6 Monate",  # wie lange
        "p": config[
            "max_age"
        ],  # Nur WG-Angebote berücksichtigen, die nicht älter sind als max_age Tage
    }


if __name__ == "__main__":
    # load data from config file:
    with open("config.yml", "r") as config_file:
        CONFIG = yaml.safe_load(config_file)

    BASE_URL = "http://www.wgcompany.de/"
    QUERY_URL = urljoin(BASE_URL, "cgi-bin/zquery.pl")

    params = generate_params_from_config(CONFIG)

    listings_request = requests.post(QUERY_URL, data=params)
    soup = BeautifulSoup(listings_request.text, "html.parser")
    ad_rows = [row for row in soup.find_all("tr") if len(row) == 7]

    for row in ad_rows:
        # Filter invalid rows:
        td_elements = row.select("td")
        link_element = td_elements[2].find("a", recursive=False)
        if not link_element or not link_element.get("href").startswith(
            "/cgi-bin/wg.pl"
        ):
            print("ERROR: link element missing or invalid")
            continue

        ad = get_data_from_row_element(row) | get_detail_from_ad_url(
            link_element.get("href")
        )
        print(ad)
        break
