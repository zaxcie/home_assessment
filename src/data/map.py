from src.utils import append_variable_to_url, download_img_from_url
from src.data.config import GOOGLE_MAP_API_KEY, GOOGLE_MAP_API_STATICMAP_URL

import os


def download_google_satellite_img(addr, url_vars=None, save_dir="data/sat_img/"):
    '''
    :param addr:
    :param url_vars:
    :return:
    '''
    if url_vars is None:
        url_vars = {"zoom": "20",
                    "size": "450x450",
                    "maptype": "satellite",
                    "key": GOOGLE_MAP_API_KEY}

    url_vars.update({"center": addr})

    img_url = append_variable_to_url(GOOGLE_MAP_API_STATICMAP_URL, url_vars)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    download_img_from_url(img_url, save_dir + addr + ".jpg")
