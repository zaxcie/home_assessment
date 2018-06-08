from src.data.duproprio import *
from src.data.map import download_google_satellite_img

import os
import json


if __name__ == '__main__':
    PROCESSED_PATH = "data/processed/"
    for file in os.listdir(PROCESSED_PATH):
        file_path = PROCESSED_PATH + file

        with open(file_path, "r") as f:
            duproprio_metadata = json.load(f)

        duproprio_building = DuProprioBuilding(duproprio_metadata)
        addr_url_escaped = duproprio_building.get_url_escaped_addr()

        download_google_satellite_img(addr_url_escaped)
