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
#import time
import argparse
import pandas as pd
from craigslist import (CraigslistGigs, CraigslistJobs, CraigslistCommunity, 
                        CraigslistServices, CraigslistEvents)
#pd.set_option('display.max_colwidth', 100)
#pd.set_option('display.max_columns', None)
#pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

# def make_clickable(val):
#    return f'<a href="{val}">{val}</a>'

words_to_omit = ['model','masseuse','massage','actress','cosplay',
                 'sexy','adult','seeking female','lonely','m4m',
                 'spanking','busty','mature','nude','mistress',
                 'Are you tired?','couple','attractive'
                ]

if __name__=='__main__':
    parser = argparse.ArgumentParser(
    description="check craigslist")
    parser.add_argument("-l", "--location", type=str, default='tokyo') #site
    parser.add_argument("-g", "--gigs", action="store_true", default=False)
    parser.add_argument("-j", "--jobs", action="store_true", default=False)
    parser.add_argument("-c", "--community", action="store_true", default=False)
    parser.add_argument("-e", "--events", action="store_true", default=False)
    parser.add_argument("-s", "--services", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    parser.add_argument("--save", action="store_true", default=False)    
    parser.add_argument("-a", "--area", type=str, default=None) #site
    parser.add_argument("-n", type=int, default=-1)
    args = parser.parse_args(None if sys.argv[1:] else ["-h"])

    if args.verbose:
        msg= "Querying craigslist: "
        print(msg)

    drop_columns = ['id','repost_of','datetime','price','geotag','has_image','where']

    if args.gigs:
        msg+=" Gigs"
        info = CraigslistGigs(site=args.location)
        drop_columns.append('is_paid') 
    elif args.jobs:
        msg+=" Jobs"
        info = CraigslistJobs(site=args.location,
                              # filters={'is_internship': False, 
                              # 'employment_type': ['full-time', 'part-time']
                              # }
                             )
        #drop_columns.append()
    elif args.community:
        msg+=" Community"
        info = CraigslistCommunity(site=args.location)
        #drop_columns.append()  
    elif args.events:
        msg+=" Events"
        info = CraigslistEvents(site=args.location,
                                #filters={'free': True, 
                                #         'food': True
                                #        }
                                )
        #print(info.show_filters())
        #drop_columns.append()
    elif args.services:
        info = CraigslistServices(site=args.location)
        #drop_columns.append()
    else:
        raise ValueError("use -g | -j | -s")

    entries = []
    for i in info.get_results(sort_by='newest'):
        entries.append(i)

    df = pd.DataFrame(entries)
    df = df.drop(drop_columns, axis=1)
    # replace capital letters
    d = df.name.apply(lambda x: x.lower())
    # remove words
    idx = d.str.contains('|'.join(words_to_omit))
    df = df[~idx].reset_index(drop=True)
    assert len(df)>0, "No data."
    #print(df.style.format({'url': make_clickable}))
    if args.n==-1:
        #pd.set_option('display.max_rows', df.shape[0]+1)
        pd.set_option('display.max_rows', None)
    #df.style.set_properties(subset=['url'], **{'width': '500px'})
    print(msg)
    print(df)
    if args.save:
        #add date
        df.to_csv('cl.csv', index=False)
