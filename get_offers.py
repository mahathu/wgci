import os, json, requests
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
        "filtered": any(w in description.lower() for w in blacklist),
    }


if __name__ == "__main__":
    ROOMS_RANGE = 2, 7
    RENT_RANGE = 200, 700
    ROOM_SQM_RANGE = 10, 40
    MAX_DAYS_AGO = 7
    LONG_TERM = True

    BASE_URL = "http://www.wgcompany.de/"
    query_url = urljoin(BASE_URL, "cgi-bin/zquery.pl")
    blacklist = ["cis", "flint", "queer", "pronomen"]

    params = {
        "st": "1",  # Verstecktes input-Feld, wenn es fehlt liefert zquery.pl ein leeres Ergebnis zurück
        "r": "1",  # Anzahl Zimmer gesucht
        "g": [str(i) for i in range(ROOMS_RANGE[0], ROOMS_RANGE[1] + 1)],  # WG-Größe
        "b": RENT_RANGE[0],  # min rent
        "a": RENT_RANGE[1],  # max rent
        "c": ROOM_SQM_RANGE[0],  # min room size
        "d": ROOM_SQM_RANGE[1],  # max room size
        "v": "dauerhaft" if LONG_TERM else "bis 6 Monate",  # wie lange
        "p": MAX_DAYS_AGO,  # Nur WG-Angebote berücksichtigen, die nicht älter sind als in Tagen
    }
    r = requests.post(query_url, data=params)
    soup = BeautifulSoup(r.text, "html.parser")
    ad_rows = [row for row in soup.find_all("tr") if len(row) == 7]

    for row in ad_rows:
        td_elements = row.select("td")
        link_element = td_elements[2].find("a", recursive=False)
        if not link_element or not link_element.get("href").startswith(
            "/cgi-bin/wg.pl"
        ):
            print("no link element")
            continue

        ad = get_data_from_row_element(row) | get_detail_from_ad_url(
            link_element.get("href")
        )
        print(ad)
        break
