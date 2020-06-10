# craigslist-cli
[![Build Status](https://travis-ci.com/jpdeleon/chronos.svg?branch=master)](https://travis-ci.com/jpdeleon/craigslist)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

scrape data from craigslist via CLI

## examples
* get posts (gigs, jobs, etc) in Manila and print summary on terminal
```bash
./posts.py -g -l manila -v 
```
![img](gigs_manila.png)

* get apartments in Tokyo by scraping the first page (-n=1) and show boxplot
```bash
./apartments.py -l tokyo -n 1 -b -v 
```
![img](./tokyo_apartments_boxplot.png)

## See also
* [octoparse](https://www.octoparse.com/tutorial-7/scraping-info-from-craigslist)
