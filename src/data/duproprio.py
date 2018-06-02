from __future__ import print_function

import requests
from bs4.element import Tag, NavigableString
from bs4 import BeautifulSoup
import copy
import json
import uuid
import pymp
import os

from src.utils import append_variable_to_url, download_img_from_url


class DuProprioScraper:

    def __init__(self,
                 base_page="https://duproprio.com/en/search/list",
                 base_image_url="https://photos.duproprio.com/",
                 default_img_save_path="data/img/",
                 default_data_path="data/processed/"):
        self.base_page = base_page
        self.base_search_var = {"sort": "-published_at",
                                "search": "true",
                                "is_for_sale": "0",
                                "with_builders": "0",
                                "parent": "1",
                                "pageNumber": 1}
        self.base_image_url = base_image_url
        self.default_img_save_path = default_img_save_path
        self.data_path = default_data_path

        self.cache_urls, self.addr_faulty_urls, self.map_url_uuid = self._cache()
        print("Caching completed")

    def create_url_for_search_page(self):
        variables = copy.deepcopy(self.base_search_var)
        variables["pageNumber"] = str(variables["pageNumber"])

        url = append_variable_to_url(self.base_page, variables)

        self.base_search_var["pageNumber"] += 1

        return url

    @staticmethod
    def find_building_page_in_search_page(search_url):
        search_page = requests.get(search_url)

        soup = BeautifulSoup(search_page.content, 'html.parser')

        findings = soup.find_all('a', class_=
                                 'gtm-search-results-link-property search-results-listings-list__item-image-link')

        building_pages = list()
        for finding in findings:
            building_pages.append(finding.attrs["href"])

        return building_pages

    def parse_building_page(self, url):
        def parse_core_property_features(soup):
            # TODO implement
            # listing-main-characteristics__title
            core_features = dict()

            dimension_items = soup.find_all('div', class_="listing-main-characteristics__item-dimensions")

            for dim_item in dimension_items:
                #listing-main-characteristics__number listing-main-characteristics__number--dimensions
                title = str(dim_item.find_all("span", class_="listing-main-characteristics__title")[0].contents[0]).strip(' \t\n\r')
                value = str(dim_item.find("span", class_="listing-main-characteristics__number listing-main-characteristics__number--dimensions").contents[0]).strip(' \t\n\r')

                if title == "Lot dimensions" or title == "Living space area (basement exclu.)":
                    try:
                        dim = {"ft": value.split("ft")[0].strip(' \t\n\r'),
                               "m": value.split("(")[1].strip(' \t\n\r m²)'),
                               "default": value}

                        core_features[title] = dim
                    except Exception as e:
                        core_features[title] = value
                else:
                    core_features[title] = value

            char_items = soup.find_all("div", class_="listing-main-characteristics__label")
            for char_item in char_items:
                title = str(char_item.find("span", class_="listing-main-characteristics__title").contents[0]).strip(' \t\n\r')
                value = str(char_item.find("span", class_="listing-main-characteristics__number").contents[0]).strip(' \t\n\r')

                core_features[title] = value

            return core_features

        def parse_property_features(soup):
            '''
            Parse Property features on top ie. Building dimensions, Backyard Faces, Year of construction, etc
            :param soup:
            :return:
            '''
            # TODO Value of fields are still raw ie Asking Price is $100,000 instead of 100000
            property_features = dict()
            property_features_table = soup_building_page.find_all("div", class_="listing-list-characteristics__table")

            for prop_feat in property_features_table:
                label = prop_feat.find("div", class_="listing-list-characteristics__row listing-list-characteristics__row--label").contents[0]
                value = prop_feat.find("div", class_="listing-list-characteristics__row listing-list-characteristics__row--value").contents[0]

                if label == "Building dimensions":
                    dim = {"Default": value,
                           "ft": value.split(" ft")[0],
                           "m": value.split("(")[1].strip(' \t\n\r)m')}

                    property_features[label] = dim
                elif label == "Asking Price":
                    property_features[label] = value.strip(' \t\n\r$')
                else:
                    property_features[label] = value

            return property_features

        def parse_extended_property_features(soup):
            '''
            Parse extended property features, ie External facing, Floor coverings, etc
            :param soup:
            :return:
            '''
            ext_prop_feat_soup = soup.find_all('div',
                                               class_="listing-complete-list-characteristics__content__group")
            ext_prop_features = dict()
            for feat in ext_prop_feat_soup:
                feature_title = feat.find('h4',
                                                  class_="listing-complete-list-characteristics__content__group__title").contents[0]
                ext_prop_feat_items = []
                for li in feat.find_all('li', class_="listing-complete-list-characteristics__content__group__item"):
                    ext_prop_feat_items.append(li.contents[0])
                ext_prop_features[feature_title] = ext_prop_feat_items

            return ext_prop_features

        def parse_costs(soup):
            '''
            Parse Cost table. School taxes, Electricity, etc
            :param soup:
            :return:
            '''
            # TODO need to parse text properly
            cost_table = soup.find_all('div', class_="mortgage-data__table__row")
            costs = dict()
            for div in cost_table:
                cost_item = \
                div.find("div", "mortgage-data__table__row__item mortgage-data__table__row__item--name").contents[0]

                cost_item = cost_item.strip(' \t\n\r')

                cost_item_month_resultset = div.find("div",
                                                     "mortgage-data__table__row__item mortgage-data__table__row__item--monthly-costs")
                if cost_item_month_resultset is None:
                    cost_item_month = None
                else:
                    cost_item_month = str(cost_item_month_resultset.contents[0]).strip(' \t\n\r$')

                cost_item_year_resultset = div.find("div",
                                                    "mortgage-data__table__row__item mortgage-data__table__row__item--yearly-costs")
                if cost_item_year_resultset is None:
                    cost_item_year = None
                else:
                    cost_item_year = str(cost_item_month_resultset.contents[0]).strip(' \t\n\r$')

                costs[cost_item] = {"cost_per_month": cost_item_month,
                                    "cost_per_year": cost_item_year}

            return costs

        def parse_price(soup):
            prices = {"Currency": soup.find('meta', property="priceCurrency").attrs["content"],
                      "Price": soup.find('meta', property="price").attrs["content"]}
            return prices

        def parse_address(soup):
            addr_tag = soup_building_page.find('div', class_="listing-location__group-address")
            address = dict()

            for addr_prop in addr_tag.find_all("meta"):
                address[addr_prop.attrs["property"]] = addr_prop.attrs["content"]

            return {"addr": address}

        def download_images(soup, save_path):
            # TODO Should valide it's always position 30 in findings to avoid computation
            # TODO add logging in downloads
            findings = soup_building_page.find_all('script')
            image_names = set()
            for finding in findings:
                script_items = finding.text.split('"')
                for i in script_items:
                    if i.endswith(".jpg") and "-1600-" in i:
                        image_names.add(i)

            for img_name in image_names:
                self.download_images(img_name, save_path)

            return image_names

        # Download page HTML
        building_page = requests.get(url)
        page_id = uuid.uuid4()
        # TODO add browser confusion here
        soup_building_page = BeautifulSoup(building_page.content, 'html.parser')

        page_metadata = dict()

        try:
            core_property = parse_core_property_features(soup_building_page)
            page_metadata.update(core_property)
        except Exception as e:
            pass

        try:
            property_features = parse_property_features(soup_building_page)
            page_metadata.update(property_features)
        except Exception as e:
            pass

        try:
            extended_property_features = parse_extended_property_features(soup_building_page)
            page_metadata.update(extended_property_features)
        except Exception as e:
            pass

        try:
            building_costs = parse_costs(soup_building_page)
            page_metadata.update(building_costs)
        except Exception as e:
            pass

        try:
            building_price = parse_price(soup_building_page)
            page_metadata.update(building_price)
        except Exception as e:
            pass

        try:
            address = parse_address(soup_building_page)
            page_metadata.update(address)
        except Exception as e:
            pass

        try:
            img_names = download_images(soup_building_page, self.default_img_save_path)
            page_metadata.update({"img_names": list(img_names)})
        except Exception as e:
            pass

        page_metadata.update({"page_id": str(page_id),
                              "url": str(url)})

        with open("data/processed/" + str(page_id) + ".json", "w") as f:
            json.dump(page_metadata, f)

    def download_images(self, img_name, save_path=None):
        '''
        Download an image from DuProprio.
        :param img_name:
        :param save_path:
        :return:
        '''

        if save_path is None:
            save_path = self.default_img_save_path

        img_url = self.base_image_url + img_name
        img_path = save_path + img_name

        download_img_from_url(img_url, img_path)

        return

    def process_page(self, thread=4):
        for i in range(2300):
            try:
                search_url = self.create_url_for_search_page()
                urls = self.find_building_page_in_search_page(search_url)

                with pymp.Parallel(thread) as p:
                    for url in p.iterate(urls):
                        if (url not in self.cache_urls) and (url not in self.addr_faulty_urls):
                            try:
                                self.parse_building_page(url)
                                message = "New url: " + url
                                p.print(message)
                            except Exception as e:
                                print(e)
                        elif url in self.addr_faulty_urls:
                            try:
                                self.parse_building_page(url)
                                message = "Update addr: " + url
                                p.print(message)
                            except Exception as e:
                                print(e)
                        else:
                            message = "Already cached: " + url
                            p.print(message)

            except Exception as e:
                print(e)

    def _cache(self, ):
        urls = set()
        # Temp cache
        faulty_addr_url = set()
        map_url_uuid = dict()

        for file_path in os.listdir(self.data_path):
            with open(self.data_path + file_path, "r") as f:
                building_data = json.load(f)

                urls.add(building_data["url"])

                if building_data.get("addressCountry") is not None:
                    faulty_addr_url.add(building_data["url"])

                map_url_uuid[building_data["url"]] = building_data["page_id"]

        return urls, faulty_addr_url, map_url_uuid

    def get_satellite_view_for_building(self):
        # TODO implement
        pass


class DuProprioBuilding:
    def __init__(self, path_json):
        self.path_json = path_json
        with open(self.path_json, "r") as f:
            self.data = json.load(f)

    def get_url_escaped_addr(self):
        #addr =
        pass

if __name__ == '__main__':
    parser = DuProprioScraper()
    parser.process_page()
