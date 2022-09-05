#!/usr/bin/env python
"""
script to print a summary of gigs in craigslist

Created on Tue May 12, 2020
@author: jpdeleon

See:
CraigslistCommunity (craigslist.org > community)
CraigslistHousing (craigslist.org > housing)
CraigslistJobs (craigslist.org > jobs)
CraigslistForSale (craigslist.org > for sale)
CraigslistEvents (craigslist.org > event calendar)
CraigslistServices (craigslist.org > services)
CraigslistGigs (craigslist.org > gigs)
CraigslistResumes (craigslist.org > resumes)
"""
import sys

# import time
import argparse
import pandas as pd
from datetime import datetime
from craigslist import (
    CraigslistGigs,
    CraigslistJobs,
    CraigslistCommunity,
    CraigslistServices,
    CraigslistEvents,
)

# pd.set_option('display.max_colwidth', 100)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
pd.set_option("display.max_colwidth", 999)

# def make_clickable(val):
#    return f'<a href="{val}">{val}</a>'

# thirty_days_old = datetime.now()
words_to_omit = [
    "AV",
    "model",
    "masseuse",
    "massage",
    "actress",
    "cosplay",
    "sexy",
    "adult",
    "bj",
    "dick",
    "seeking female",
    "lonely",
    "m4m",
    "spanking",
    "busty",
    "mature",
    "nude",
    "mistress",
    "Are you tired?",
    "couple",
    "attractive",
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="check craigslist")
    parser.add_argument("-l", "--location", type=str, default="tokyo")  # site
    parser.add_argument("-g", "--gigs", action="store_true", default=False)
    parser.add_argument("-j", "--jobs", action="store_true", default=False)
    parser.add_argument(
        "-c", "--community", action="store_true", default=False
    )
    parser.add_argument("-e", "--events", action="store_true", default=False)
    parser.add_argument("-s", "--services", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    parser.add_argument("--save", action="store_true", default=False)
    parser.add_argument("-a", "--area", type=str, default=None)  # site
    # parser.add_argument("-d", type=str, default=thirty_days_old)
    parser.add_argument("-k", "--keywords", nargs='+', type=str, default=None)
    parser.add_argument("-n", type=int, default=None)
    args = parser.parse_args(None if sys.argv[1:] else ["-h"])

    drop_columns = [
        "id",
        "repost_of",
        "datetime",
        "price",
        "geotag",
        "has_image",
        "where",
    ]
    location = args.location.lower()

    if args.gigs:
        msg = (
            f"Querying gigs from https://{location}.craigslist.org/search/ggg?"
        )
        info = CraigslistGigs(site=location)
        drop_columns.append("is_paid")
    elif args.jobs:
        msg = (
            f"Querying jobs from https://{location}.craigslist.org/search/jjj?"
        )
        info = CraigslistJobs(
            site=location,
            # filters={'is_internship': False,
            # 'employment_type': ['full-time', 'part-time']
            # }
        )
        # drop_columns.append()
    elif args.community:
        msg = f"Querying community from https://{location}.craigslist.org/search/ccc?"
        info = CraigslistCommunity(site=location)
        # drop_columns.append()
    elif args.events:
        msg = f"Querying events from https://{location}.craigslist.org/search/eee?"
        info = CraigslistEvents(
            site=location,
            # filters={'free': True,
            #         'food': True
            #        }
        )
        # print(info.show_filters())
        # drop_columns.append()
    elif args.services:
        msg = f"Querying services from https://{location}.craigslist.org/search/sss?"
        info = CraigslistServices(site=location)
        # drop_columns.append()
    else:
        raise ValueError("use -g | -j | -s")
    if args.verbose:
        print(msg)

    entries = []
    for i in info.get_results(sort_by="newest"):
        entries.append(i)

    df = pd.DataFrame(entries)
    df = df.drop(drop_columns, axis=1)
    # replace capital letters
    d = df.name.apply(lambda x: x.lower())
    # remove words
    idx = d.str.contains("|".join(words_to_omit), case=False)
    df = df[~idx].reset_index(drop=True)
    assert len(df) > 0, "No data."
    # print(df.style.format({'url': make_clickable}))
    if args.n is None:
        # pd.set_option('display.max_rows', df.head(args.n))
        pd.set_option("display.max_rows", 999)
    # df.style.set_properties(subset=['url'], **{'width': '500px'})
    if args.keywords is not None:
        #import pdb; pdb.set_trace()
        idx = df.name.str.contains('|'.join(args.keywords), case=False)
    if len(df[idx])>0:
        df = df[idx]
    else:
        print(f"{args.keywords} not found from the following:")
    print(df)
    if args.save:
        # add date
        df.to_csv("cl.csv", index=False)
