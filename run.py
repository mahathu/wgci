import locale
import logging
import sys
from wgcompanyWatcher import WGCompanyWatcher


def set_up_logging():
    logging.basicConfig(
        filename="logfile.log",
        encoding="utf-8",
        level=logging.INFO,
        format="[%(asctime)s] %(message)s",
        datefmt="%m-%d-%Y %H:%M:%S",
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


if __name__ == "__main__":
    set_up_logging()

    locale.setlocale(locale.LC_ALL, "de_DE")

    app = WGCompanyWatcher()
    app.run()
