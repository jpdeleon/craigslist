#!/usr/bin/env python
"""
scrape apartment data from craiglist

code larged based from:
https://towardsdatascience.com/web-scraping-craigslist-a-complete-tutorial-c41cea4f4981

Created on Tue May 12, 2020
@author: jpdeleon
"""
import sys
import argparse
from time import sleep
import re
from random import randint
from warnings import warn
from time import time
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as pl
import seaborn as sb
from tqdm import tqdm

pl.style.use("default")
# pl.style.use("fivethirtyeight")
# params = {'legend.fontsize': 'x-large',
#           'figure.figsize': (15, 5),
#          'axes.labelsize': 'x-large',
#          'axes.titlesize':'x-large',
#          'xtick.labelsize':'x-large',
#          'ytick.labelsize':'x-large'}
# pl.rcParams.update(params)


currency = {"tokyo": "¥", "seoul": "₩", "manila": "₱", "sfbay": "$"}


class Base:
    def __init__(
        self,
        location,
        max_price=1000000,
        max_sqft=None,
        verbose=True,
        npages=None,
        save_csv=False,
        save_fig=False,
    ):
        self.location = location
        self.currency_mark = currency[self.location]
        self.max_price = max_price
        self.max_sqft = max_sqft
        self.npages = npages
        self.verbose = verbose
        self.save_csv = save_csv
        self.save_fig = save_fig
        self.post_timing = []
        self.post_hoods = []
        self.post_title_texts = []
        self.bedroom_counts = []
        self.sqfts = []
        self.post_links = []
        self.post_prices = []
        # methods
        self.scrape_craiglist()
        self.apts = self.make_df()

    def get_pages(self):
        # get the first page of housing prices
        response = response = requests.get(
            f"https://{self.location}.craigslist.org/search/apa/apt?"
            + "&hasPic=1"
            + "&availabilityMode=0"
            + "&sale_date=all+dates"
        )
        # parse html
        html_soup = BeautifulSoup(response.text, "html.parser")

        # find the total number of posts to find the limit of the pagination
        results_num = html_soup.find("div", class_="search-legend")
        results_total = int(
            results_num.find("span", class_="totalcount").text
        )  # pulled the total count of posts as the upper bound of the pages array

        # each page has 119 posts so each new page is defined as follows: s=120, s=240, s=360, and so on.
        # so we need to step in size 120 in the np.arange function
        pages = np.arange(0, results_total + 1, 120)
        # if self.verbose:
        #    print(f"Found {results_total} pages.")
        return pages

    def scrape_craiglist(self):
        if self.npages is None:
            pages = self.get_pages()
        else:
            pages = np.arange(1, self.npages + 1)
        if self.verbose:
            print(
                f"Scraping {len(pages)} out of {len(self.get_pages())} pages."
            )

        for page in tqdm(pages):

            # get request
            response = requests.get(
                f"https://{self.location}.craigslist.org/search/apa/apt?"
                + "s="  # the parameter for defining the page number
                + str(page)  # the page number in the pages array from earlier
                + "&hasPic=1"
                + "&availabilityMode=0"
                + "&sale_date=all+dates"
            )

            sleep(randint(1, 5))

            # throw warning for status codes that are not 200
            if response.status_code != 200:
                warn(
                    "Request: {}; Status code: {}".format(
                        requests, response.status_code
                    )
                )

            # define the html text
            page_html = BeautifulSoup(response.text, "html.parser")

            # define the posts
            posts = page_html.find_all("li", class_="result-row")

            # extract data item-wise
            for post in posts:
                # try:
                if post.find("span", class_="result-hood") is not None:

                    # posting date
                    # grab the datetime element 0 for date and 1 for time
                    post_datetime = post.find("time", class_="result-date")[
                        "datetime"
                    ]
                    self.post_timing.append(post_datetime)

                    # neighborhoods
                    post_hood = post.find("span", class_="result-hood").text
                    self.post_hoods.append(post_hood)

                    # title text
                    post_title = post.find("a", class_="result-title hdrlnk")
                    post_title_text = post_title.text
                    self.post_title_texts.append(post_title_text)

                    # post link
                    post_link = post_title["href"]
                    self.post_links.append(post_link)

                    # removes the \n whitespace from each side, removes the currency symbol, and turns it into an int
                    post_price = int(
                        post.a.text.strip().replace(self.currency_mark, "")
                    )
                    self.post_prices.append(post_price)

                    if post.find("span", class_="housing") is not None:

                        # if the first element is accidentally square footage
                        if (
                            "ft2"
                            in post.find(
                                "span", class_="housing"
                            ).text.split()[0]
                        ):

                            # make bedroom nan
                            bedroom_count = np.nan
                            self.bedroom_counts.append(bedroom_count)

                            # make sqft the first element
                            sqft = post.find(
                                "span", class_="housing"
                            ).text.split()[0][:-3]
                            # sqft = int(sqft)
                            self.sqfts.append(sqft)

                        # if the length of the housing details element is more than 2
                        elif (
                            len(
                                post.find(
                                    "span", class_="housing"
                                ).text.split()
                            )
                            > 2
                        ):

                            # therefore element 0 will be bedroom count
                            bedroom_count = (
                                post.find("span", class_="housing")
                                .text.replace("br", "")
                                .split()[0]
                            )
                            self.bedroom_counts.append(bedroom_count)

                            # and sqft will be number 3, so set these here and append
                            sqft = post.find(
                                "span", class_="housing"
                            ).text.split()[2][:-3]
                            # sqft = int(sqft)
                            self.sqfts.append(sqft)

                        # if there is num bedrooms but no sqft
                        elif (
                            len(
                                post.find(
                                    "span", class_="housing"
                                ).text.split()
                            )
                            == 2
                        ):

                            # therefore element 0 will be bedroom count
                            bedroom_count = (
                                post.find("span", class_="housing")
                                .text.replace("br", "")
                                .split()[0]
                            )
                            self.bedroom_counts.append(bedroom_count)

                            # and sqft will be number 3, so set these here and append
                            sqft = np.nan
                            self.sqfts.append(sqft)

                        else:
                            bedroom_count = np.nan
                            self.bedroom_counts.append(bedroom_count)

                            sqft = np.nan
                            self.sqfts.append(sqft)

                    # if none of those conditions catch, make bedroom nan, this won't be needed
                    else:
                        bedroom_count = np.nan
                        self.bedroom_counts.append(bedroom_count)

                        sqft = np.nan
                        self.sqfts.append(sqft)
                    #    bedroom_counts.append(bedroom_count)

                    #    sqft = np.nan
                    #    sqfts.append(sqft)
                # except Exception as e:
                #     print(e)
            # print("Page " + str(iterations+1) + " scraped successfully.")

        print("\n")

    def make_df(self):
        df = pd.DataFrame(
            {
                "posted": self.post_timing,
                "neighborhood": self.post_hoods,
                "post title": self.post_title_texts,
                "number bedrooms": self.bedroom_counts,
                "sqft": self.sqfts,
                "URL": self.post_links,
                "price": self.post_prices,
            }
        )
        df["number bedrooms"] = pd.to_numeric(
            df["number bedrooms"], errors="coerce"
        )
        df["sqft"] = pd.to_numeric(df["sqft"], errors="coerce")
        if self.save_csv:
            fp = f"{self.location}_apartments.csv"
            df.to_csv(fp, index=False)
        return df

    def plot_price(self, ax=None):
        apts = self.apts.copy()
        assert apts is not None, "Empty data!"
        if ax is None:
            fig, ax = pl.subplots(
                1, 1, figsize=(12, 8), constrained_layout=True
            )

        sb.scatterplot(
            x="price",
            y="sqft",
            hue="number bedrooms",
            palette="viridis",
            x_jitter=True,
            y_jitter=True,
            s=125,
            data=apts[
                (apts.price < self.max_price) & (apts.sqft < self.max_sqft)
            ],
            ax=ax,
        )
        ax.set_xlabel(f"Price ({self.currency_mark})")
        ax.set_ylabel("Area (sqft)")
        ax.set_title(f"Apartments in {self.location}")
        if self.save_fig:
            fp = f"{self.location}_apartments_price.png"
            fig.savefig(fp)
        return ax

    def plot_regression(self, ax=None):
        apts = self.apts.copy()
        assert apts is not None, "Empty data!"
        if ax is None:
            fig, ax = pl.subplots(
                1, 1, figsize=(12, 8), constrained_layout=True
            )
        sb.regplot(
            x="price",
            y="sqft",
            data=apts[
                (apts.price < self.max_price) & (apts.sqft < self.max_sqft)
            ],
            ax=ax,
        )
        ax.set_xlabel(f"Price ({self.currency_mark})")
        ax.set_ylabel("Area (sqft)")
        ax.set_title(f"Apartments in {self.location}")
        if self.save_fig:
            fp = f"{self.location}_apartments_regression.png"
            fig.savefig(fp)
        return ax

    def plot_boxplot(self, ax=None):
        apts = self.apts.copy()
        assert apts is not None, "Empty data!"
        if ax is None:
            fig, ax = pl.subplots(
                1, 1, figsize=(12, 8), constrained_layout=True
            )
        #
        apts.neighborhood = apts.neighborhood.apply(lambda x: x.lower())
        # remove parentheses, site/ location, numbers
        apts.neighborhood = apts.neighborhood.apply(
            lambda x: x.replace("(", "")
        )
        apts.neighborhood = apts.neighborhood.apply(
            lambda x: x.replace(")", "")
        )
        apts.neighborhood = apts.neighborhood.apply(
            lambda x: x.replace(f", {self.location}", "")
        )
        apts.neighborhood = apts.neighborhood.apply(
            lambda x: x.replace(f" and ", "&")
        )
        apts.neighborhood = apts.neighborhood.apply(
            lambda x: "".join([i for i in x if not i.isdigit()])
        )
        apts.neighborhood = apts.neighborhood.apply(
            lambda x: x.replace(f" line", "")
        )
        apts.neighborhood = apts.neighborhood.apply(
            lambda x: x.replace(f" station", "")
        )
        if self.location == "seoul":
            apts.neighborhood = apts.neighborhood.apply(
                lambda x: x.replace(f" stn", "")
            )
            apts.neighborhood = apts.neighborhood.apply(
                lambda x: x.replace(f" subway", "")
            )
        if self.location == "tokyo":
            apts.neighborhood = apts.neighborhood.apply(
                lambda x: x.replace(f" city", "")
            )
            apts.neighborhood = apts.neighborhood.apply(
                lambda x: x.replace(f"-ku", "")
            )
        min_count = 2 if self.npages == 1 else 5
        # apts2 = apts.groupby(by='neighborhood').filter(lambda x, min_count=min_count: len(x) >= min_count if len(str(x).split())<3 else False)
        apts2 = apts.groupby(by="neighborhood").filter(
            lambda x, min_count=min_count: len(x) >= min_count
        )
        sb.boxplot(
            x="neighborhood",
            y="price",
            data=apts2[
                (apts2.price < self.max_price) & (apts2.sqft < self.max_sqft)
            ],
        )
        pl.xticks(rotation=75)
        ax.set_ylabel(f"Price ({self.currency_mark})")
        ax.set_xlabel("Neighborhood")
        ax.set_title(f"Apartments in {self.location}")
        if self.save_fig:
            fp = f"{self.location}_apartments_boxplot.png"
            fig.savefig(fp)
        return ax


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="check craigslist apartments")
    parser.add_argument("-l", "--location", type=str, default="tokyo")  # site
    parser.add_argument("--max_price", type=float, default=100000)
    parser.add_argument("--max_sqft", type=float, default=100)
    parser.add_argument("-n", "--npages", type=int, default=None)
    parser.add_argument(
        "-p", "--show_price", action="store_true", default=False
    )
    parser.add_argument(
        "-r", "--show_regression", action="store_true", default=False
    )
    parser.add_argument(
        "-b", "--show_boxplot", action="store_true", default=False
    )
    parser.add_argument("--save_csv", action="store_true", default=False)
    parser.add_argument("--save_fig", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    args = parser.parse_args(None if sys.argv[1:] else ["-h"])

    bc = Base(
        location=args.location,
        max_price=args.max_price,
        max_sqft=args.max_sqft,
        verbose=args.verbose,
        npages=args.npages,
        save_csv=args.save_csv,
        save_fig=args.save_fig,
    )
    if args.show_price:
        ax = bc.plot_price()
        pl.show()
    if args.show_regression:
        ax = bc.plot_regression()
        pl.show()
    if args.show_boxplot:
        ax = bc.plot_boxplot()
        pl.show()
