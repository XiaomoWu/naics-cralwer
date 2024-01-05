import pandas as pd
import scrapy

from pathlib import Path


class QuotesSpider(scrapy.Spider):
    name = "naics"

    def start_requests(self):
        years = [2012, 2017, 2022]
        two_digits = [
            11,
            21,
            22,
            23,
            31,
            32,
            33,
            42,
            44,
            45,
            48,
            49,
            51,
            52,
            53,
            54,
            55,
            56,
            61,
            62,
            71,
            72,
            81,
            92,
        ]

        for year in years:
            for two_digit in two_digits:
                url = (
                    f"https://www.naics.com/six-digit-naics/?v={year}&code={two_digit}"
                )

                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={"two_digit": two_digit, "year": year},
                )

    def parse(self, response):
        two_digit = response.meta["two_digit"]
        year = response.meta["year"]

        # --- 4 digits ---#
        rows = response.xpath('//summary[contains(@class, "headersum")]')

        naics_4d = []
        for row in rows:
            code = row.xpath('.//div[@class="naicscode"]/strong/text()').get().strip()
            desc = row.xpath('.//div[@class="naicstit"]/strong/text()').get().strip()

            naics_4d.append({"year": year, "code": code, "desc": desc, "level": "4 digits"})
        naics_4d = pd.DataFrame(naics_4d)

        # --- 6 digits ---#
        rows = response.xpath('//div[@class="encl"]')

        naics_6d = []
        for row in rows:
            code = row.xpath('.//div[@class="sixlink naicscode"]/a/text()').get().strip()
            desc = row.xpath('.//div[@class="sixlink naicstit"]/a/text()').get().strip()

            naics_6d.append({"year": year, "code": code, "desc": desc, "level": "6 digits"})
        naics_6d = pd.DataFrame(naics_6d)

        # --- merge and save these two dataframes ---#
        naics = pd.concat([naics_4d, naics_6d], ignore_index=True)

        # if the "code" field only has two digits, then change the "level" to "2 digits"
        naics.loc[naics["code"].str.len() == 2, "level"] = "2 digits"

        naics.to_feather(f"results/by-year/naics_{year}_{two_digit}.feather")
